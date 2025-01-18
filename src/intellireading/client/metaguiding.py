import logging
from io import BytesIO
import os
from intellireading.client.regex import RegExBoldMetaguider
import zipfile
from typing import Generator


_logger = logging.getLogger(__name__)
_metaguider = RegExBoldMetaguider()
_METAGUIDED_FLAG_FILENAME = "intellireading.metaguide"


class _EpubItemFile:
    _logger = logging.getLogger(__name__)

    def __init__(self, filename: str | None = None, content: bytes = b"") -> None:
        self.filename = filename
        self.content = content
        _extension = (self.filename and os.path.splitext(self.filename)[-1].upper()) or None

        # some epub have files with html extension but they are xml files
        self.is_xhtml_document = _extension in (".HTM", ".HTML", ".XHTML")
        self.metaguided = False  # flag to indicate if the file has been metaguided. Useful for multi-threading

    def __str__(self) -> str:
        return f"{self.filename} ({len(self.content)} bytes)"

    def metaguide(self, metaguider: RegExBoldMetaguider):
        if self.metaguided:
            self._logger.warning("File %s already metaguided, skipping", self.filename)
        elif self.is_xhtml_document:
            self._logger.debug("Process (begin): %s", self.filename)
            self.content = metaguider.metaguide_xhtml_document(self.content)
            self.metaguided = True
            self._logger.debug("Process (end): %s", self.filename)
        else:
            self._logger.debug("Skipping file %s", self.filename)


def _get_epub_item_files_from_zip(input_zip: zipfile.ZipFile) -> list:
    def _read_compressed_file(input_zip: zipfile.ZipFile, filename: str) -> _EpubItemFile:
        return _EpubItemFile(filename, input_zip.read(filename))

    _epub_item_files = [_read_compressed_file(input_zip, f.filename) for f in input_zip.infolist()]
    _logger.debug("Read %d files from input file", len(_epub_item_files))
    return _epub_item_files


def _process_epub_item_files(epub_item_files: list[_EpubItemFile]) -> Generator[_EpubItemFile, None, None]:
    for _epub_item_file in epub_item_files:
        _logger.debug(f"Processing file '{_epub_item_file.filename}'")
        _epub_item_file.metaguide(_metaguider)
        yield _epub_item_file


def _write_item_files_to_zip(epub_item_files, output_zip):
    def _write_compressed_file(output_zip: zipfile.ZipFile, epub_item_file: _EpubItemFile):
        if epub_item_file.filename is None:
            msg = "EpubItemFile.filename is None"
            raise ValueError(msg)

        _logger.debug(
            "Writing file %s to output zip %s",
            epub_item_file.filename,
            output_zip.filename,
        )
        with output_zip.open(epub_item_file.filename, mode="w") as _compressed_output_file:
            _compressed_output_file.write(epub_item_file.content)

    for _epub_item_file in epub_item_files:
        _write_compressed_file(output_zip, _epub_item_file)


def metaguide_epub(input_stream: BytesIO) -> BytesIO:
    """Metaguide an epub file
    input_file_stream: BytesIO
        The input epub file stream
    return: BytesIO
        The metaguided epub file stream
    """
    output_stream = BytesIO()

    _logger.debug("Metaguiding epub: Getting item files")
    with zipfile.ZipFile(input_stream, "r", compression=zipfile.ZIP_DEFLATED, allowZip64=True) as input_zip:
        with zipfile.ZipFile(output_stream, "w", compression=zipfile.ZIP_DEFLATED, allowZip64=True) as output_zip:
            _logger.debug("Processing zip: Getting item files")
            _epub_item_files = _get_epub_item_files_from_zip(input_zip)

            # check if we have _METAGUIDED_FLAG_FILENAME in the epub
            # if we do, this file has been metaguided already
            if any(f.filename == _METAGUIDED_FLAG_FILENAME for f in _epub_item_files):
                _logger.debug("Epub already metaguided, skipping...")
                # copy the input stream to the output stream
                input_stream.seek(0)
                output_stream.write(input_stream.read())
            else:
                processed_item_files = _process_epub_item_files(_epub_item_files)
                _logger.debug("Processing zip: Writing output zip")
                _write_item_files_to_zip(processed_item_files, output_zip)
                # write the metaguided file flag to the zip
                output_zip.writestr(_METAGUIDED_FLAG_FILENAME, b"")

    output_stream.seek(0)
    return output_stream


def metaguide_xhtml(input_file_stream: BytesIO) -> BytesIO:
    """Metaguide an xhtml file
    input_file_stream: BytesIO
        The input xhtml file stream
    return: BytesIO
        The metaguided xhtml file stream
    """
    output_file_stream = BytesIO()
    output_file_stream.write(_metaguider.metaguide_xhtml_document(input_file_stream.read()))
    output_file_stream.seek(0)
    return output_file_stream


def metaguide_dir(input_dir: str, output_dir: str) -> None:
    """Metaguides all epubs and xhtml found in a directory (recursively)
    input_dir: str
        The input epub/xhtml directory
    output_dir: str
        The output epub/xhtml directory
    """

    # get a list of all the files in the directory, and the child directories if recursive
    # verify if the file is a file and if it has the correct extension
    def _get_files(directory, recursive):
        for filename in os.listdir(directory):
            input_filename = os.path.join(directory, filename)

            extension = os.path.splitext(input_filename)[-1].upper()
            if os.path.isfile(input_filename) and (extension in [".EPUB", "*.KEPUB", ".XHTML", ".HTML", ".HTM"]):
                yield input_filename
            elif os.path.isdir(input_filename) and recursive:
                yield from _get_files(input_filename, recursive)

    _logger.info(
        "Processing files in %s to %s (recursively)",
        input_dir,
        output_dir,
    )

    files_processed = 0
    files_skipped = 0
    files_with_errors = 0

    # check if the output directory exists and if not create it
    if not os.path.exists(output_dir):
        _logger.info("Creating %s", output_dir)
        os.makedirs(output_dir)

    for input_filename in _get_files(input_dir, True):
        output_filename = os.path.join(output_dir, os.path.basename(input_filename))

        _logger.debug("Processing %s to %s", input_filename, output_filename)

        # verify if the output file already exists
        if os.path.isfile(output_filename):
            _logger.warning("Skipping %s because %s already exists", input_filename, output_filename)
            files_skipped += 1
            continue

        try:
            with open(input_filename, "rb") as input_reader:
                input_file_stream = BytesIO(input_reader.read())
                if input_filename.upper().endswith(".EPUB") or input_filename.upper().endswith(".KEPUB"):
                    output_file_stream = metaguide_epub(input_file_stream)
                else:
                    output_file_stream = metaguide_xhtml(input_file_stream)
                with open(output_filename, "wb") as output_writer:
                    output_writer.write(output_file_stream.read())
            files_processed += 1
        except Exception as e:  # pylint: disable=broad-except
            # pylint: disable=logging-fstring-interpolation
            files_with_errors += 1
            _logger.exception(f"Error processing {input_filename}", e)
            continue

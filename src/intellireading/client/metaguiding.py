import logging
from io import BytesIO
import os
from intellireading.client.regex import RegExBoldMetaguider
import zipfile
from typing import Generator


_logger = logging.getLogger(__name__)
_metaguider = RegExBoldMetaguider()
_METAGUIDED_FLAG_FILENAME = "intellireading.metaguide"
_EPUB_EXTENSIONS = [".EPUB", ".KEPUB"]
_XHTML_EXTENSIONS = [".XHTML", ".HTML", ".HTM"]


class _EpubItemFile:
    _logger = logging.getLogger(__name__)

    def __init__(self, filename: str | None = None, content: bytes = b"") -> None:
        self.filename = filename
        self.content = content
        _extension = (self.filename and os.path.splitext(self.filename)[-1].upper()) or None

        # some epub have files with html extension but they are xml files
        self.is_xhtml_document = _extension in _XHTML_EXTENSIONS
        self.metaguided = False  # flag to indicate if the file has been metaguided. Useful for multi-threading

    def __str__(self) -> str:
        return f"{self.filename} ({len(self.content)} bytes)"

    def metaguide(self, metaguider: RegExBoldMetaguider, *, remove_metaguiding: bool = False):
        if not remove_metaguiding and self.metaguided:
            self._logger.warning("File %s already metaguided, skipping", self.filename)
        elif self.is_xhtml_document:
            self._logger.debug("Metaguide (begin): %s", self.filename)
            self.content = metaguider.metaguide_xhtml_document(self.content, remove_metaguiding=remove_metaguiding)
            self.metaguided = True
            self._logger.debug("Metaguide (end): %s", self.filename)
        else:
            self._logger.debug("Skipping file %s", self.filename)


def _get_epub_item_files_from_zip(input_zip: zipfile.ZipFile) -> list:
    def read_compressed_file(input_zip: zipfile.ZipFile, filename: str) -> _EpubItemFile:
        return _EpubItemFile(filename, input_zip.read(filename))

    epub_item_files = [read_compressed_file(input_zip, f.filename) for f in input_zip.infolist()]
    _logger.debug("Read %d files from input file", len(epub_item_files))
    return epub_item_files


def _process_epub_item_files(
    epub_item_files: list[_EpubItemFile], *, remove_metaguiding: bool = False
) -> Generator[_EpubItemFile, None, None]:
    for epub_item_file in epub_item_files:
        _logger.debug(f"Processing file '{epub_item_file.filename}' remove_metaguiding={remove_metaguiding}")
        epub_item_file.metaguide(_metaguider, remove_metaguiding=remove_metaguiding)
        yield epub_item_file


def _write_item_files_to_zip(epub_item_files, output_zip):
    def write_compressed_file(output_zip: zipfile.ZipFile, epub_item_file: _EpubItemFile):
        if epub_item_file.filename is None:
            msg = "EpubItemFile.filename is None"
            raise ValueError(msg)

        _logger.debug(
            "Writing file %s to output zip %s",
            epub_item_file.filename,
            output_zip.filename,
        )
        with output_zip.open(epub_item_file.filename, mode="w") as compressed_output_file:
            compressed_output_file.write(epub_item_file.content)

    for _epub_item_file in epub_item_files:
        write_compressed_file(output_zip, _epub_item_file)


def metaguide_epub(input_stream: BytesIO, *, remove_metaguiding: bool = False) -> BytesIO:
    """Metaguide an epub file
    input_file_stream: BytesIO
        The input epub file stream
    remove_metaguiding: bool
        If True, removes metaguiding from the epub file
    return: BytesIO
        The metaguided epub file stream
    """
    output_stream = BytesIO()

    if remove_metaguiding:
        _logger.debug("Removing metaguiding from epub")
    else:
        _logger.debug("Metaguiding epub")

    _logger.debug("Getting item files")
    with zipfile.ZipFile(input_stream, "r", compression=zipfile.ZIP_DEFLATED, allowZip64=True) as input_zip:
        with zipfile.ZipFile(output_stream, "w", compression=zipfile.ZIP_DEFLATED, allowZip64=True) as output_zip:
            _logger.debug("Processing zip: Getting item files")
            epub_item_files = _get_epub_item_files_from_zip(input_zip)

            # check if we are metaguiding and have _METAGUIDED_FLAG_FILENAME in the epub
            # if we do, this file has been metaguided already
            if not remove_metaguiding and any(f.filename == _METAGUIDED_FLAG_FILENAME for f in epub_item_files):
                _logger.debug("Epub already metaguided, skipping...")
                # copy the input stream to the output stream
                input_stream.seek(0)
                output_stream.write(input_stream.read())
            else:
                processed_item_files = list(
                    _process_epub_item_files(epub_item_files, remove_metaguiding=remove_metaguiding)
                )

                if remove_metaguiding:
                    # remove the metaguided flag file
                    filtered_files = filter(lambda f: f.filename != _METAGUIDED_FLAG_FILENAME, processed_item_files)
                    processed_item_files = list(filtered_files)
                else:
                    _logger.debug("Processing zip: Adding metaguided flag file")
                    processed_item_files.append(_EpubItemFile(_METAGUIDED_FLAG_FILENAME))

                _logger.debug("Processing zip: Writing output zip")
                _write_item_files_to_zip(processed_item_files, output_zip)

    output_stream.seek(0)
    return output_stream


def metaguide_xhtml(input_file_stream: BytesIO, *, remove_metaguiding: bool = False) -> BytesIO:
    """Metaguide an xhtml file
    input_file_stream: BytesIO
        The input xhtml file stream
    remove_metaguiding: bool
        If True, removes metaguiding from the xhtml file
    return: BytesIO
        The metaguided xhtml file stream
    """
    output_file_stream = BytesIO()
    output_file_stream.write(
        _metaguider.metaguide_xhtml_document(input_file_stream.read(), remove_metaguiding=remove_metaguiding)
    )
    output_file_stream.seek(0)
    return output_file_stream


def metaguide_dir(input_dir: str, output_dir: str, *, remove_metaguiding: bool = False):
    """Metaguides all epubs and xhtml found in a directory (recursively)
    input_dir: str
        The input epub/xhtml directory
    output_dir: str
        The output epub/xhtml directory
    remove_metaguiding: bool
        If True, removes metaguiding from the files
    """

    # get a list of all the files in the directory, and the child directories if recursive
    # verify if the file is a file and if it has the correct extension
    def get_files(directory, recursive):
        for filename in os.listdir(directory):
            input_filename = os.path.join(directory, filename)

            extension = os.path.splitext(input_filename)[-1].upper()
            if os.path.isfile(input_filename) and (extension in _EPUB_EXTENSIONS or extension in _XHTML_EXTENSIONS):
                yield input_filename
            elif os.path.isdir(input_filename) and recursive:
                yield from get_files(input_filename, recursive)

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

    for input_filename in get_files(input_dir, True):
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
                if os.path.splitext(input_filename)[-1].upper() in _EPUB_EXTENSIONS:
                    output_file_stream = metaguide_epub(input_file_stream, remove_metaguiding=remove_metaguiding)
                else:
                    output_file_stream = metaguide_xhtml(input_file_stream, remove_metaguiding=remove_metaguiding)
                with open(output_filename, "wb") as output_writer:
                    output_writer.write(output_file_stream.read())
            files_processed += 1
        except Exception as e:  # pylint: disable=broad-except
            # pylint: disable=logging-fstring-interpolation
            files_with_errors += 1
            _logger.exception(f"Error processing {input_filename}", e)
            continue

from click.testing import CliRunner
from intellireading.client.commands import metaguide_epub_cmd, metaguide_xhtml_cmd, metaguide_dir_cmd
from intellireading.client.metaguiding import _METAGUIDED_FLAG_FILENAME
import os


def test_metaguide_epub_cmd():
    runner = CliRunner()

    # get the epub test file path from the tests folder
    epub_test_file = os.path.join(os.path.dirname(__file__), "test_files", "input.epub")

    with runner.isolated_filesystem():

        # Run the command
        result = runner.invoke(metaguide_epub_cmd, ["--input_file", epub_test_file, "--output_file", "output.epub"])

        # Check the output
        assert result.exit_code == 0

        # Check that the output file was created
        assert os.path.exists("output.epub")

        # open the output zip file and check that the metaguide flag file was created
        import zipfile

        with zipfile.ZipFile("output.epub", "r") as zip_ref:
            zip_ref.extractall("output")
            flag_file_path = f"output/{_METAGUIDED_FLAG_FILENAME}"
            assert os.path.exists(flag_file_path)


def test_metaguide_xhtml_cmd():
    runner = CliRunner()

    # get the epub test file path from the tests folder
    xhtml_test_file = os.path.join(os.path.dirname(__file__), "test_files", "input.xhtml")

    with runner.isolated_filesystem():

        # Run the command
        result = runner.invoke(metaguide_xhtml_cmd, ["--input_file", xhtml_test_file, "--output_file", "output.xhtml"])

        # Check the output
        assert result.exit_code == 0

        # Check that the output file was created
        assert os.path.exists("output.xhtml")


def test_metaguide_dir_cmd():
    runner = CliRunner()

    # get the epub test file path from the tests folder
    test_dir = os.path.join(os.path.dirname(__file__), "test_files")

    with runner.isolated_filesystem():

        # Run the command
        result = runner.invoke(metaguide_dir_cmd, ["--input_dir", test_dir, "--output_dir", "output"])

        # Check the output
        assert result.exit_code == 0

        # Check that the output file was created
        assert os.path.exists("output/input.epub")
        assert os.path.exists("output/input.xhtml")

        # open the output zip file and check that the metaguide flag file was created
        import zipfile

        with zipfile.ZipFile("output/input.epub", "r") as zip_ref:
            zip_ref.extractall("output")
            flag_file_path = f"output/{_METAGUIDED_FLAG_FILENAME}"
            assert os.path.exists(flag_file_path)

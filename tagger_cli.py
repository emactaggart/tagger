from tagger.cmd import create_backup, generate_metadata_tags_from_library, apply_renaming_to_files, restore_metadata_tags_from_backup
import click


@click.group()
@click.pass_context
def main(ctx):
    ...


@main.command(
    short_help="Create a backup of the existing metadata tags from all of the audio files contained within a given library."
)
@click.option("--type", type=click.Choice(["mixxx"]), help="Type of library (which dj software).")
@click.option("--libpath", help="location of dj softare library.")
@click.option("--output-dir", help="Json backup output dir.")
@click.pass_context
def backup(ctx, type, libpath, output_dir):
    """
    # FIXME deal with missing/hidden files
    """
    create_backup(type, libpath, output_dir)
    # create_backup(library_type, library_path, output_filename)
    ...


@main.command(
    short_help="Generate metadata tags according to the organization of a library's crates and save them to a json file."
)
@click.option("--type", type=click.Choice(["mixxx"]), help="Type of library (which dj software).")
@click.option("--libpath", help="location of dj softare library.")
@click.option("--output-dir", help="Json file output dir.")
@click.pass_context
def make_tags(
    ctx, type, libpath, output_dir
):
    """
    """
    generate_metadata_tags_from_library(type, libpath, output_dir)
    ...


@main.command(
    short_help="Restore/apply/write all of the metadata tags contained within a given json file to the corresponding audio files."
)
@click.option("--json-file", help="Json file.")
@click.pass_context
def apply(ctx, json_file):
    """
    # FIXME deal with missing/hidden/moved files
    """
    restore_metadata_tags_from_backup(json_file)
    ...


@main.command(
    short_help="Rename files using the updated `filename` metadata field in a given json file."
)
@click.option("--json-file", help="Json file.")
@click.pass_context
def rename(ctx, json_file):
    """
    # FIXME deal with missing/hidden/moved files
    """
    apply_renaming_to_files(json_file)
    ...


def start():
    main(obj={})


if __name__ == "__main__":
    start()

from tagger.cmd import LibraryType, create_backup, generate_metadata_tags_from_library, apply_renaming_to_files, restore_metadata_tags_from_backup
import click

import webbrowser


@click.group()
@click.pass_context
def main(ctx):
    ...


@main.command(
    short_help="Create a backup of the existing metadata tags from all of the audio files contained within a given library."
)
@click.option("--type", "-t", type=click.Choice(LibraryType.all()), help="Type of library (which dj software).")
@click.option("--libpath", "-l", help="location of dj softare library.")
@click.option("--output-dir", "-o", help="Json backup output dir.")
@click.pass_context
def backup(ctx, type, libpath, output_dir):
    """
    # FIXME deal with missing/hidden files
    """
    json_file =  create_backup(type, libpath, output_dir)
    click.echo(json_file)
    # create_backup(library_type, library_path, output_filename)
    ...


@main.command(
    short_help="Generate metadata tags according to the organization of a library's crates and save them to a json file."
)
@click.option("--type", '-t', type=click.Choice(LibraryType.all()), help="Type of library (which dj software).")
@click.option("--libpath", '-l', help="location of dj softare library.")
@click.option("--output-dir", '-o', help="Json file output dir.")
@click.pass_context
def make_tags(
    ctx, type, libpath, output_dir
):
    """
    """
    json_file = generate_metadata_tags_from_library(type, libpath, output_dir)
    click.echo(json_file)
    ...


@main.command(
    short_help="Restore/apply/write all of the metadata tags contained within a given json file to the corresponding audio files."
)
@click.option("--json-file", '-i', help="Json file.")
@click.option("--replacement", '-r', multiple=True, help="Tagfile path replacements.")
@click.pass_context
def apply(ctx, json_file, replacement):
    """
    # FIXME deal with missing/hidden/moved files
    # FIXME what happens when filenames have "="?
    """
    restore_metadata_tags_from_backup(json_file, path_replacements=[r.split("=")[:2] for r in replacement if "=" in r])
    ...


@main.command(
    short_help="Rename files using the updated `filename` metadata field in a given json file."
)
@click.option("--json-file", '-i', help="Json file.")
@click.pass_context
def rename(ctx, json_file):
    """
    # FIXME deal with missing/hidden/moved files
    """
    apply_renaming_to_files(json_file)
    ...


@main.command(
    short_help="View a json file."
)
@click.option("--json-file", '-i', help="Json file.")
@click.pass_context
def view(ctx, json_file):
    webbrowser.open(json_file)


def start():
    main(obj={})


if __name__ == "__main__":
    start()

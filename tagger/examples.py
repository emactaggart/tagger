

# def CommandLineInteractionExamples():
#     # FIXME might need to package tagger, or hard wire directories
#     """
#     For all commands wrap in quotes and call via python -c
#     """

#     # dir->json
#     import json, sys
#     from tagger import TaggerCommands

#     sys.stdout.write(json.dumps(TaggerCommands.read_all_tags_from_dir("%s")))
#     import json, sys
#     from tagger import TaggerCommands

#     sys.stdout.write(json.dumps(TaggerCommands.read_all_tags_from_dir("/home/evan/Downloads/")))

#     TaggerCommands.read_all_tags_from_dir("/home/evan/Downloads/")
#     dir_name = "/home/evan/Downloads/"

#     # m3u->json
#     import json, sys
#     from tagger import TaggerCommands

#     sys.stdout.write(json.dumps(TaggerCommands.tags_from_m3u("%s")))

#     # json->write-tags-to-files
#     import json, sys
#     from tagger import TaggerCommands

#     TaggerCommands.write_tags(json.loads(sys.stdin.read()))

#     # json->rename-files
#     import json, sys
#     from tagger import TaggerCommands

#     TaggerCommands.rename_files(json.loads(sys.stdin.read()))

#     # tag_m3u
#     from tagger import TaggerCommands

#     TaggerCommands.tag_comments_m3u("%s", "%s", remove_tags=False)

#     # clear_tags_m3u
#     from tagger import TaggerCommands

#     TaggerCommands.clear_comments_m3u("%s")

#     # clear_tags_dir
#     from tagger import TaggerCommands

#     TaggerCommands.clear_comments_dir("%s")

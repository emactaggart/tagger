#!/usr/bin/env ipython3


# class MixxxTests():

    # @skip
    # def mixxx_query_find_track_by location():
    #     database_filename="/home/evan/.mixxx/mixxxdb.sqlite"
    #     filename_from = "/home/evan/Desktop/MixxxTesting/test-hek.flac"
    #     filename_to = "/home/evan/Desktop/MixxxTesting/test-yek.flac"
    #     select_query = """
    # select * from track_locations
    #     where location in (:from, :to)
    #     order by id desc
    #     limit 1;
    #     """
    #     _result_= list(
    #         map(
    #             dict,
    #             _query_db(
    #                 "/home/evan/.mixxx/mixxxdb.sqlite",
    #                 select_query,
    #                 {
    #                     "from": filename_from,
    #                     "to": filename_to,
    #                 },
    #             ),
    #         )
    #     )

    #     rename_track_locations(database_filename, filename_from, filename_to)

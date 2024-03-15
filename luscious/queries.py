def artist_search_query(artist_query: str, page: int, search_query: str = '', sorting: str = 'rating_all_time') -> dict:
        """
        Build Album search query.
        :param search_query: keyword
        :param sorting:
        :param page: initial search page
        :return: Query
        """
        return {
                "operationName": "AlbumList",
                "query": """
                    query AlbumList($input: AlbumListInput!) {
                        album {
                            list(input: $input) {
                                info {...FacetCollectionInfo}
                                items {...AlbumMinimal}
                            }
                        }
                    }
                    fragment FacetCollectionInfo on FacetCollectionInfo {
                        page
                        has_next_page
                    }
                    fragment AlbumMinimal on Album {
                        __typename
                        id
                        title
                        description
                        created
                        modified
                        like_status
                        moderation_status
                        number_of_favorites
                        number_of_dislikes
                        number_of_pictures
                        number_of_animated_pictures
                        number_of_duplicates
                        slug
                        is_manga
                        url
                        download_url
                        labels
                        permissions
                        cover {
                            width
                            height
                            size
                            url
                        }
                        created_by {
                            id
                            url
                            name
                            display_name
                            user_title
                            avatar_url
                        }
                        language {
                            id
                            title
                            url
                        }
                        tags {
                            category
                            text
                            url
                            count
                        }
                        genres {
                            id
                            title
                            slug
                            url
                        }
                    }
                """,
                "variables": {
                        "input": {
                                "items_per_page": 30,
                                "display": sorting,
                                "filters": [
                                        {
                                                "name": "album_type",
                                                "value": "manga"
                                        },
                                        {
                                                "name": "audience_ids",
                                                "value": "+1+10+2+3+5+6+8+9"
                                        },
                                        {
                                                "name": "language_ids",
                                                "value": "+1"
                                        },
                                        {
                                                "name": "tagged",
                                                "value": artist_query
                                        }
                                ],
                                "page": page
                        }
                }
        }


def album_list_pictures_query(album_id: str, page_number: int) -> dict:
    """
    Build Album pictures query.
    :param album_id: Album id
    :param page_number: initial search page
    :return: Query
    """
    return {
        "operationName": "AlbumListOwnPictures",
        "query": """
            query AlbumListOwnPictures($input: PictureListInput!) {
                picture {
                    list(input: $input) {
                        info {...FacetCollectionInfo}
                        items {...PictureStandardWithoutAlbum}
                    }
                }
            }
            fragment FacetCollectionInfo on FacetCollectionInfo {
                page
                has_next_page
            }
            fragment PictureStandardWithoutAlbum on Picture {
                url_to_original
                url_to_video
                url
            }
        """,
        "variables": {
            "input": {
                "filters": [
                    {
                        "name": "album_id",
                        "value": album_id
                    }
                ],
                "display": "rating_all_time",
                "page": page_number
            }
        }
    }


def album_info_query(album_id: str) -> dict:
    """
    Build Album information query.
    :param album_id: Album id
    :return: Query
    """
    return {
        "operationName": "AlbumGet",
        "query": """
            query AlbumGet($id: ID!) {
                album {
                    get(id: $id) {
                        ... on Album {...AlbumStandard}
                        ... on MutationError {errors {code message}}
                    }
                }
            }
            fragment AlbumStandard on Album {
                id
                title
                slug
                url
                description
                created_by {
                    name
                    display_name
                }
                number_of_pictures
                number_of_animated_pictures
                language {
                    title
                }
                tags {
                    text
                }
                genres {
                    title
                }
                audiences {
                    title
                }
            }
        """,
        "variables": {
            "id": album_id
        }
    }


def album_search_query(search_query: str, album_type: str, page: int, sorting: str = 'rating_all_time') -> dict:
        """
        Build Album search query.
        :param search_query: keyword
        :param sorting:
        :param page: initial search page
        :return: Query
        """
        return {
                "operationName": "AlbumList",
                "query": """
                    query AlbumList($input: AlbumListInput!) {
                        album {
                            list(input: $input) {
                                info {...FacetCollectionInfo}
                                items {...AlbumMinimal}
                            }
                        }
                    }
                    fragment FacetCollectionInfo on FacetCollectionInfo {
                        page
                        has_next_page
                    }
                    fragment AlbumMinimal on Album {
                        __typename
                        id
                        title
                        description
                        created
                        modified
                        like_status
                        moderation_status
                        number_of_favorites
                        number_of_dislikes
                        number_of_pictures
                        number_of_animated_pictures
                        number_of_duplicates
                        slug
                        is_manga
                        url
                        download_url
                        labels
                        permissions
                        cover {
                            width
                            height
                            size
                            url
                        }
                        created_by {
                            id
                            url
                            name
                            display_name
                            user_title
                            avatar_url
                        }
                        language {
                            id
                            title
                            url
                        }
                        tags {
                            category
                            text
                            url
                            count
                        }
                        genres {
                            id
                            title
                            slug
                            url
                        }
                    }
                """,
                "variables": {
                        "input": {
                                "items_per_page": 30,
                                "display": sorting,
                                "filters": [
                                        {
                                                "name": "album_type",
                                                "value": album_type
                                        },
                                        {
                                                "name": "tagged",
                                                "value": search_query
                                        }
                                ],
                                "page": page
                        }
                }
        }
import json
import magic
import copy
from mock import Mock
from nose.tools import assert_raises, assert_equal, assert_not_equal, assert_true
from jsonschema.exceptions import ValidationError
from tests.base import BaseTestCase
from splice.ingest import ingest_links, generate_artifacts, IngestError, distribute
from splice.models import Tile, Adgroup, AdgroupSite


class TestIngestLinks(BaseTestCase):

    def test_invalid_data(self):
        """
        Invalid data is sent for ingestion
        """
        assert_raises(ValidationError, ingest_links, {"invalid": {"data": 1}}, self.channels[0].id)

    def test_empty_data(self):
        """
        Empty data input is not processed
        """
        data = ingest_links({}, self.channels[0].id)
        assert_equal(data, {})

    def test_invalid_country_code(self):
        """
        Invalid country code is rejected
        """
        assert_raises(IngestError, ingest_links, {"INVALID/en-US": [
            {
                "imageURI": "data:image/png;base64,somedata",
                "url": "https://somewhere.com",
                "title": "Some Title",
                "type": "organic",
                "bgColor": "#FFFFFF"
            }
        ]}, self.channels[0].id)

    def test_invalid_locale(self):
        """
        Invalid locale is rejected
        """
        assert_raises(IngestError, ingest_links, {"US/en-DE": [
            {
                "imageURI": "data:image/png;base64,somedata",
                "url": "https://somewhere.com",
                "title": "Some Title",
                "type": "organic",
                "bgColor": "#FFFFFF"
            }
        ]}, self.channels[0].id)

    def test_invalid_related(self):
        """
        Invalid suggested type is rejected
        """
        assert_raises(ValidationError, ingest_links, {"US/en-US": [
            {
                "imageURI": "data:image/png;base64,somedata",
                "url": "https://somewhere.com",
                "title": "Some Title",
                "type": "organic",
                "bgColor": "#FFFFFF",
                "frecent_sites": "not an array, really"
            }
        ]}, self.channels[0].id)

    def test_suggested_sites(self):
        """
        just a simple suggested site tile
        """
        tile = {
            "imageURI": "data:image/png;base64,somedata",
            "url": "https://somewhere.com",
            "title": "Some Title",
            "type": "organic",
            "bgColor": "#FFFFFF",
            "frecent_sites": ["http://abc.com", "https://xyz.com"]
        }
        c = self.env.db.session.query(Adgroup).count()
        assert_equal(30, c)
        c = self.env.db.session.query(AdgroupSite).count()
        assert_equal(0, c)
        data = ingest_links({"US/en-US": [tile]}, self.channels[0].id)
        assert_equal(1, len(data["US/en-US"]))
        c = self.env.db.session.query(Adgroup).count()
        assert_equal(31, c)
        c = self.env.db.session.query(AdgroupSite).count()
        assert_equal(2, c)

    def test_ingest_suggested_sites(self):
        """
        Test that there is no duplication when ingesting tiles
        """
        with open(self.get_fixture_path("tiles_suggested.json"), 'r') as f:
            tiles = json.load(f)

        num_tiles = self.env.db.session.query(Tile).count()
        data = ingest_links(tiles, self.channels[0].id)
        assert_equal(len(data['STAR/en-US']), 5)
        new_num_tiles = self.env.db.session.query(Tile).count()
        assert_equal(num_tiles + 4, new_num_tiles)

        # ingesting the same thing a second time should be idempotent
        data = ingest_links(tiles, self.channels[0].id)
        assert_equal(len(data['STAR/en-US']), 5)
        new_num_tiles = self.env.db.session.query(Tile).count()
        assert_equal(num_tiles + 4, new_num_tiles)

    def test_id_creation(self):
        """
        Test an id is created for a valid tile
        """
        tile = {
            "imageURI": "data:image/png;base64,somedata",
            "url": "https://somewhere.com",
            "title": "Some Title",
            "type": "organic",
            "bgColor": "#FFFFFF"
        }
        data = ingest_links({"STAR/en-US": [tile]}, self.channels[0].id)
        directory_id = data["STAR/en-US"][0]["directoryId"]

        # the biggest ID is 99 - next one should be 100
        assert_equal(100, directory_id)

    def test_id_not_duplicated(self):
        """
        Test an id is created for a valid tile
        """
        tiles_star = [
            {
                "imageURI": "data:image/png;base64,somedata",
                "url": "https://somewhere.com",
                "title": "Some Title",
                "type": "organic",
                "bgColor": "#FFFFFF"
            },
            {
                "imageURI": "data:image/png;base64,someotherdata",
                "url": "https://somewhereelse.com",
                "title": "Some Other Title",
                "type": "organic",
                "bgColor": "#FFFFFF"
            },
        ]

        tiles_ca = [
            {
                "imageURI": "data:image/png;base64,somedata",
                "url": "https://somewhere.com",
                "title": "Some Title",
                "type": "organic",
                "bgColor": "#FFFFFF"
            }
        ]
        data = ingest_links({
            "STAR/en-US": tiles_star,
            "CA/en-US": tiles_ca,
        }, self.channels[0].id)
        directory_id_star = data["STAR/en-US"][0]["directoryId"]
        directory_id_ca = data["CA/en-US"][0]["directoryId"]
        assert_equal(100, directory_id_star)
        assert_not_equal(data["STAR/en-US"][1]["directoryId"], directory_id_star)
        assert_equal(directory_id_ca, directory_id_star)

    def test_id_not_overwritten(self):
        """
        Test an id is created for a valid tile
        """
        tiles_star = [
            {
                "imageURI": "data:image/png;base64,somedata",
                "url": "https://somewhere.com",
                "title": "Some Title",
                "type": "organic",
                "bgColor": "#FFFFFF"
            }
        ]

        data = ingest_links({"STAR/en-US": tiles_star}, self.channels[0].id)
        directory_id = data["STAR/en-US"][0]["directoryId"]
        assert_equal(100, directory_id)

        data = ingest_links({"STAR/en-US": tiles_star}, self.channels[0].id)
        directory_id = data["STAR/en-US"][0]["directoryId"]
        assert_equal(100, directory_id)

    def test_error_mid_ingestion(self):
        """
        Test an error happening mid-ingestion
        """
        tiles_star = [
            {
                "imageURI": "data:image/png;base64,somedata",
                "url": "https://somewhere.com",
                "title": "Some Title",
                "type": "organic",
                "bgColor": "#FFFFFF"
            },
            {
                "imageURI": "data:image/png;base64,someotherdata",
                "url": "https://somewhereelse.com",
                "title": "Some Other Title",
                "type": "organic",
                "bgColor": "#FFFFFF"
            },
        ]
        tile_count_before = self.env.db.session.query(Tile).count()

        import splice.ingest
        insert_function = splice.ingest.insert_tile

        # put counts in a dict to get around python's
        # non-local scope restrictions on variables
        # for access in mock_ingest
        counts = {
            'call': 0,
            'exception_at': 2,
        }

        def mock_ingest(*args, **kwargs):
            counts['call'] += 1
            if counts['call'] < counts['exception_at']:
                return insert_function(*args, **kwargs)
            else:
                raise Exception('Boom')

        function_mock = Mock(side_effect=mock_ingest)
        splice.ingest.insert_tile = function_mock

        ingest_links({"STAR/en-US": tiles_star}, self.channels[0].id)
        tile_count_after = self.env.db.session.query(Tile).count()

        # only one has been inserted out of two
        assert_equal(1, tile_count_after - tile_count_before)

        # put the module function back to what it was
        splice.ingest.insert_tile = insert_function

    def test_ingest_dbpool(self):
        """
        Test a ingestion of a large number of tiles that could use up connections to the db
        """
        with open(self.get_fixture_path("2014-10-30.ja-pt.json"), 'r') as f:
            tiles = json.load(f)
        ingest_links(tiles, self.channels[0].id)
        num_tiles = self.env.db.session.query(Tile).count()
        assert(num_tiles > 30)

    def test_ingest_no_duplicates(self):
        """
        Test that there is no duplication when ingesting tiles
        """
        with open(self.get_fixture_path("tiles_duplicates.json"), 'r') as f:
            tiles = json.load(f)

        num_tiles = self.env.db.session.query(Tile).count()
        data = ingest_links(tiles, self.channels[0].id)
        new_num_tiles = self.env.db.session.query(Tile).count()
        assert_equal(num_tiles + 1, new_num_tiles)


class TestGenerateArtifacts(BaseTestCase):

    def test_generate_artifacts(self):
        """
        Tests that the correct number of artifacts are generated
        """
        with open(self.get_fixture_path("valid_tile.json"), 'r') as f:
            fixture = json.load(f)

        tile = fixture["STAR/en-US"][0]

        data = ingest_links({"STAR/en-US": [tile]}, self.channels[0].id)
        artifacts = generate_artifacts(data, self.channels[0].name, True)
        # tile index, distribution and 2 image files are generated
        assert_equal(5, len(artifacts))

        data = ingest_links({
            "STAR/en-US": [tile],
            "CA/en-US": [tile]
        }, self.channels[0].id)
        artifacts = generate_artifacts(data, self.channels[0].name, True)
        # includes one more file: the locale data payload
        assert_equal(6, len(artifacts))

    def test_unknown_mime_type(self):
        """
        Tests that an unknown mime type is rejected
        """
        tiles_star = [
            {
                "imageURI": "data:image/weirdimage;base64,somedata",
                "url": "https://somewhere.com",
                "title": "Some Title",
                "type": "organic",
                "bgColor": "#FFFFFF"
            }
        ]

        data = ingest_links({"STAR/en-US": tiles_star}, self.channels[0].id)
        assert_raises(IngestError, generate_artifacts, data, self.channels[0].name, True)

    def test_malformed_data_uri_meta(self):
        """
        Tests that a malformed data uri declaration is rejected
        """
        tiles_star = [
            {
                "imageURI": "data:image/somedata",
                "url": "https://somewhere.com",
                "title": "Some Title",
                "type": "organic",
                "bgColor": "#FFFFFF"
            }
        ]

        data = ingest_links({"STAR/en-US": tiles_star}, self.channels[0].id)
        assert_raises(IngestError, generate_artifacts, data, self.channels[0].name, True)

    def test_image_content(self):
        with open(self.get_fixture_path("valid_tile.json"), 'r') as f:
            tiles = json.load(f)
        data = ingest_links(tiles, self.channels[0].id)
        artifacts = generate_artifacts(data, self.channels[0].name, True)

        found_image = False
        for file in artifacts:
            if "mime" in file:
                found_image = True
                assert_equal(file["mime"], magic.from_buffer(file["data"], mime=True))

        assert_true(found_image)

    def test_image_artifact_hash(self):
        """
        Test that the correct number of image artifacts are produced
        """
        with open(self.get_fixture_path("valid_tile.json"), 'r') as f:
            fixture = json.load(f)

        tile_1 = fixture["STAR/en-US"][0]

        tile_2 = copy.deepcopy(tile_1)
        tile_2['title'] = 'Some Other Title'

        tile_3 = copy.deepcopy(tile_1)
        tile_3['title'] = 'Yet Another Title'

        tiles = {'STAR/en-US': [tile_1, tile_2, tile_3]}
        data = ingest_links(tiles, self.channels[0].id)
        artifacts = generate_artifacts(data, self.channels[0].name, True)

        # even if there are 3 tiles, there should only be 2 images
        image_count = 0
        for a in artifacts:
            mime = a.get('mime')
            if mime and mime == 'image/png':
                image_count += 1

        assert_equal(2, image_count)


class TestDistribute(BaseTestCase):

    def setUp(self):
        import splice.ingest

        self.key_mock = Mock()
        self.bucket_mock = Mock()

        def bucket_get_key_mock(*args, **kwargs):
            return None
        self.bucket_mock.get_key = Mock(side_effect=bucket_get_key_mock)

        def get_key_mock(*args, **kwargs):
            return self.key_mock
        splice.ingest.Key = Mock(side_effect=get_key_mock)

        def get_bucket_mock(*args, **kwargs):
            return self.bucket_mock
        self.env.s3.get_bucket = Mock(side_effect=get_bucket_mock)

        super(TestDistribute, self).setUp()

    def test_distribute(self):
        tiles_star = [
            {
                "imageURI": "data:image/png;base64,somedata",
                "enhancedImageURI": "data:image/png;base64,somemoredata",
                "url": "https://somewhere.com",
                "title": "Some Title",
                "type": "organic",
                "bgColor": "#FFFFFF"
            }
        ]

        tiles_ca = [
            {
                "imageURI": "data:image/png;base64,somedata",
                "url": "https://somewhere.com",
                "title": "Some Title",
                "type": "organic",
                "bgColor": "#FFFFFF"
            }
        ]

        data = ingest_links({"STAR/en-US": tiles_star}, self.channels[0].id)
        distribute(data, self.channels[0].id, True)
        # 5 files are uploaded, mirrors generate artifactes
        assert_equal(5, self.key_mock.set_contents_from_string.call_count)

        self.key_mock.set_contents_from_string = Mock()
        data = ingest_links({
            "STAR/en-US": tiles_star,
            "CA/en-US": tiles_ca,
        }, self.channels[0].id)
        distribute(data, self.channels[0].id, True)
        #  includes one more upload: the locate data payload
        assert_equal(6, self.key_mock.set_contents_from_string.call_count)

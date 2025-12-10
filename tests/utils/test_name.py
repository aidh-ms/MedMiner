"""Tests for name conversion utilities."""

import pytest

from medminer.utils.name import NameMixin, camel_to_snake


class TestCamelToSnake:
    """Test cases for camel_to_snake function."""

    def test_simple_camel_case(self) -> None:
        """Test conversion of simple CamelCase strings."""
        assert camel_to_snake("MyClassName") == "my_class_name"
        assert camel_to_snake("SimpleTest") == "simple_test"
        assert camel_to_snake("UserProfile") == "user_profile"

    def test_single_word(self) -> None:
        """Test conversion of single word strings."""
        assert camel_to_snake("Name") == "name"
        assert camel_to_snake("Test") == "test"
        assert camel_to_snake("Workflow") == "workflow"

    def test_all_caps_acronyms(self) -> None:
        """Test conversion of strings with all-caps acronyms."""
        assert camel_to_snake("HTTPServer") == "http_server"
        assert camel_to_snake("XMLParser") == "xml_parser"
        assert camel_to_snake("JSONData") == "json_data"
        assert camel_to_snake("APIHandler") == "api_handler"

    def test_consecutive_capitals(self) -> None:
        """Test conversion of strings with consecutive capital letters."""
        assert camel_to_snake("HTMLParser") == "html_parser"
        assert camel_to_snake("URLPath") == "url_path"
        assert camel_to_snake("IOError") == "io_error"

    def test_numbers_in_name(self) -> None:
        """Test conversion of strings containing numbers."""
        assert camel_to_snake("Version2Handler") == "version2_handler"
        assert camel_to_snake("Test123Class") == "test123_class"
        assert camel_to_snake("HTTP2Server") == "http2_server"

    def test_already_lowercase(self) -> None:
        """Test conversion of already lowercase strings."""
        assert camel_to_snake("lowercase") == "lowercase"
        assert camel_to_snake("alreadysnake") == "alreadysnake"

    def test_already_snake_case(self) -> None:
        """Test that snake_case strings remain unchanged."""
        assert camel_to_snake("already_snake_case") == "already_snake_case"
        assert camel_to_snake("my_function_name") == "my_function_name"

    def test_empty_string(self) -> None:
        """Test conversion of empty string."""
        assert camel_to_snake("") == ""

    def test_mixed_patterns(self) -> None:
        """Test conversion of strings with mixed patterns."""
        assert camel_to_snake("GetHTTPResponseCode") == "get_http_response_code"
        assert camel_to_snake("HTTPSConnectionPool") == "https_connection_pool"
        assert camel_to_snake("MyHTTPSServer") == "my_https_server"

    def test_trailing_caps(self) -> None:
        """Test conversion of strings ending with capitals."""
        assert camel_to_snake("ParseHTML") == "parse_html"
        assert camel_to_snake("SaveJSON") == "save_json"

    def test_single_letter(self) -> None:
        """Test conversion of single letter strings."""
        assert camel_to_snake("A") == "a"
        assert camel_to_snake("Z") == "z"


class TestNameMixin:
    """Test cases for NameMixin class."""

    def test_simple_class_name(self) -> None:
        """Test NameMixin with simple class name."""

        class MyWorkflow(NameMixin):
            pass

        assert MyWorkflow().name == "my_workflow"

    def test_single_word_class(self) -> None:
        """Test NameMixin with single word class name."""

        class Extractor(NameMixin):
            pass

        assert Extractor().name == "extractor"

    def test_acronym_class_name(self) -> None:
        """Test NameMixin with acronym in class name."""

        class HTTPHandler(NameMixin):
            pass

        assert HTTPHandler().name == "http_handler"

    def test_complex_class_name(self) -> None:
        """Test NameMixin with complex class name."""

        class MedicationExtractionWorkflow(NameMixin):
            pass

        assert MedicationExtractionWorkflow().name == "medication_extraction_workflow"

    def test_name_property_is_readonly(self) -> None:
        """Test that name property cannot be set directly."""

        class TestClass(NameMixin):
            pass

        instance = TestClass()
        with pytest.raises(AttributeError):
            instance.name = "new_name"  # type: ignore[misc]

    def test_multiple_instances_same_name(self) -> None:
        """Test that multiple instances return the same name."""

        class SampleClass(NameMixin):
            pass

        instance1 = SampleClass()
        instance2 = SampleClass()

        assert instance1.name == instance2.name == "sample_class"

    def test_inheritance_uses_actual_class(self) -> None:
        """Test that name property uses the actual class name, not parent."""

        class BaseClass(NameMixin):
            pass

        class DerivedClass(BaseClass):
            pass

        assert BaseClass().name == "base_class"
        assert DerivedClass().name == "derived_class"

    def test_with_numbers_in_class_name(self) -> None:
        """Test NameMixin with numbers in class name."""

        class Workflow2024(NameMixin):
            pass

        assert Workflow2024().name == "workflow2024"

    def test_with_all_caps_class_name(self) -> None:
        """Test NameMixin with all caps acronym class name."""

        class XMLParser(NameMixin):
            pass

        assert XMLParser().name == "xml_parser"

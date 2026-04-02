"""Tests for raml_examples fixtures."""

import os
import pytest
from ramlpy.api import parse, parse_string
from ramlpy.loader.version import detect_raml_version

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "fixtures", "raml_examples")


# =============================================================================
# simple-08 tests
# =============================================================================

class TestSimple08:
    """Tests for simple-08/api.raml - Basic RAML 0.8 API."""
    
    @pytest.fixture
    def api(self):
        return parse(os.path.join(FIXTURES_DIR, "simple-08", "api.raml"))
    
    def test_version(self):
        path = os.path.join(FIXTURES_DIR, "simple-08", "api.raml")
        with open(path) as f:
            assert detect_raml_version(f.read()) == "0.8"
    
    def test_title(self, api):
        assert api.title == "Simple User API"
    
    def test_version_field(self, api):
        assert api.version == "v1"
    
    def test_base_uri(self, api):
        assert api.base_uri == "https://api.example.com/{version}"
    
    def test_media_type(self, api):
        assert api.media_type == "application/json"
    
    def test_resources_count(self, api):
        assert len(api.resources) == 2
    
    def test_users_resource(self, api):
        resource = api.resource("/users")
        assert resource.full_path == "/users"
        assert "get" in resource.methods
        assert "post" in resource.methods
    
    def test_users_by_id_resource(self, api):
        resource = api.resource("/users/{userId}")
        assert resource.full_path == "/users/{userId}"
        assert "get" in resource.methods
    
    def test_users_get_query_params(self, api):
        resource = api.resource("/users")
        method = resource.method("get")
        assert "limit" in method.query_parameters
        limit_param = method.query_parameters["limit"]
        assert limit_param.type_ref == "integer"
        assert limit_param.default == 20
        assert limit_param.minimum == 1
        assert limit_param.maximum == 100
    
    def test_users_by_id_uri_param(self, api):
        resource = api.resource("/users/{userId}")
        assert "userId" in resource.uri_parameters
        uri_param = resource.uri_parameters["userId"]
        assert uri_param.type_ref == "integer"
        assert uri_param.required is True
    
    def test_schemas(self, api):
        assert "User" in api.types
        assert "NewUser" in api.types
    
    def test_validate_users_list_request(self, api):
        result = api.validate_request(
            path="/users",
            method="get",
            path_params={},
            query_params={"limit": "50"},
            headers={},
            body=None,
            content_type=None,
        )
        assert result.ok
        assert result.data["query_params"]["limit"] == 50
    
    def test_validate_users_list_invalid_limit(self, api):
        result = api.validate_request(
            path="/users",
            method="get",
            path_params={},
            query_params={"limit": "abc"},
            headers={},
            body=None,
            content_type=None,
        )
        assert not result.ok
        assert any(e["code"] == "invalid_type" for e in result.errors)


# =============================================================================
# simple-10-inline tests
# =============================================================================

class TestSimple10Inline:
    """Tests for simple-10-inline/api.raml - RAML 1.0 with inline types."""
    
    @pytest.fixture
    def api(self):
        return parse(os.path.join(FIXTURES_DIR, "simple-10-inline", "api.raml"))
    
    def test_version(self):
        path = os.path.join(FIXTURES_DIR, "simple-10-inline", "api.raml")
        with open(path) as f:
            assert detect_raml_version(f.read()) == "1.0"
    
    def test_title(self, api):
        assert api.title == "Simple Product API"
    
    def test_types(self, api):
        assert "Product" in api.types
        assert "ProductCreateRequest" in api.types
    
    def test_product_type_has_properties(self, api):
        product_type = api.types["Product"]
        assert product_type.base_type == "object"
        assert "id" in product_type.properties
        assert "name" in product_type.properties
        assert "category" in product_type.properties
        assert "price" in product_type.properties
    
    def test_products_resource(self, api):
        resource = api.resource("/products")
        assert resource.full_path == "/products"
        assert "get" in resource.methods
        assert "post" in resource.methods
    
    def test_products_by_id_resource(self, api):
        resource = api.resource("/products/{productId}")
        assert resource.full_path == "/products/{productId}"
        assert "get" in resource.methods
    
    def test_products_get_query_params(self, api):
        resource = api.resource("/products")
        method = resource.method("get")
        assert "category" in method.query_parameters
        assert "limit" in method.query_parameters
    
    def test_validate_products_list_request(self, api):
        result = api.validate_request(
            path="/products",
            method="get",
            path_params={},
            query_params={"limit": "20"},
            headers={},
            body=None,
            content_type=None,
        )
        assert result.ok
        assert result.data["query_params"]["limit"] == 20


# =============================================================================
# simple-10-with-types tests
# =============================================================================

class TestSimple10WithTypes:
    """Tests for simple-10-with-types/api.raml - RAML 1.0 with external types."""
    
    @pytest.fixture
    def api(self):
        return parse(os.path.join(FIXTURES_DIR, "simple-10-with-types", "api.raml"))
    
    def test_title(self, api):
        assert api.title == "Customer API"
    
    def test_resources(self, api):
        assert len(api.resources) == 2
    
    def test_customers_resource(self, api):
        resource = api.resource("/customers")
        assert resource.full_path == "/customers"
        assert "get" in resource.methods
        assert "post" in resource.methods
    
    def test_customers_by_id_resource(self, api):
        resource = api.resource("/customers/{customerId}")
        assert resource.full_path == "/customers/{customerId}"
        assert "get" in resource.methods
    
    def test_validate_customers_list_request(self, api):
        result = api.validate_request(
            path="/customers",
            method="get",
            path_params={},
            query_params={"email": "test@example.com"},
            headers={},
            body=None,
            content_type=None,
        )
        assert result.ok


# =============================================================================
# simple-08-with-types tests
# =============================================================================

class TestSimple08WithTypes:
    """Tests for simple-08-with-types/api.raml - RAML 0.8 with external schemas."""
    
    @pytest.fixture
    def api(self):
        return parse(os.path.join(FIXTURES_DIR, "simple-08-with-types", "api.raml"))
    
    def test_title(self, api):
        assert api.title == "Simple Users API"
    
    def test_resources(self, api):
        assert len(api.resources) >= 1


# =============================================================================
# complex-08-with-types tests
# =============================================================================

class TestComplex08WithTypes:
    """Tests for complex-08-with-types/api.raml - Complex RAML 0.8 with includes."""
    
    @pytest.fixture
    def api(self):
        return parse(os.path.join(FIXTURES_DIR, "complex-08-with-types", "api.raml"))
    
    def test_title(self, api):
        assert api.title == "Orders API"
    
    def test_version(self, api):
        assert api.version == "v1"
    
    def test_base_uri(self, api):
        assert api.base_uri == "https://orders.example.com/{version}"
    
    def test_resources(self, api):
        assert len(api.resources) >= 1
    
    def test_orders_resource(self, api):
        resource = api.resource("/orders")
        assert resource.full_path == "/orders"
    
    def test_security_schemes(self, api):
        assert len(api.security_schemes) > 0


# =============================================================================
# complex-10-with-types tests
# =============================================================================

class TestComplex10WithTypes:
    """Tests for complex-10-with-types/api.raml - Complex RAML 1.0 with traits."""
    
    @pytest.fixture
    def api(self):
        return parse(os.path.join(FIXTURES_DIR, "complex-10-with-types", "api.raml"))
    
    def test_title(self, api):
        assert api.title == "Order Management API"
    
    def test_version(self, api):
        assert api.version == "v1"
    
    def test_resources(self, api):
        assert len(api.resources) >= 1
    
    def test_orders_resource(self, api):
        resource = api.resource("/orders")
        assert resource.full_path == "/orders"
        assert "get" in resource.methods
    
    def test_security_schemes(self, api):
        assert "bearerAuth" in api.security_schemes
    
    def test_traits(self, api):
        assert "pageable" in api.traits
        assert "traceable" in api.traits


# =============================================================================
# modular-10-library tests
# =============================================================================

class TestModular10Library:
    """Tests for modular-10-library/api.raml - RAML 1.0 with library uses."""
    
    @pytest.fixture
    def api(self):
        return parse(os.path.join(FIXTURES_DIR, "modular-10-library", "api.raml"))
    
    def test_title(self, api):
        assert api.title == "Billing API"
    
    def test_version(self, api):
        assert api.version == "v1"
    
    def test_resources(self, api):
        assert len(api.resources) == 2
    
    def test_invoices_resource(self, api):
        resource = api.resource("/invoices")
        assert resource.full_path == "/invoices"
        assert "get" in resource.methods
        assert "post" in resource.methods
    
    def test_customers_resource(self, api):
        resource = api.resource("/customers/{customerId}")
        assert resource.full_path == "/customers/{customerId}"
        assert "get" in resource.methods

-- Create test database for pytest
CREATE DATABASE easyaccounting_test OWNER easy_owner;
GRANT CONNECT ON DATABASE easyaccounting_test TO easy_app, easy_auth;

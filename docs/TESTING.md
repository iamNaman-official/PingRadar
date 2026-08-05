# 🧪 PingRadar Testing

## Overview

PingRadar uses Django's built-in testing framework to verify application behavior and maintain reliability as the project evolves.

The testing strategy focuses on validating:

- Database model behavior
- User authentication flows
- Website ownership protection
- View functionality
- Website management operations
- Monitoring data storage

The goal of testing is not only to check that the application works, but also to ensure future changes do not break existing functionality.

---

# 🛠️ Testing Stack

PingRadar uses the following tools:

| Tool | Purpose |
|---|---|
| Django TestCase | Application and database testing |
| Django Client | Simulating browser requests |
| Assertions | Validating expected behavior |
| GitHub Actions | Automated CI testing |
| Ruff | Code quality checks |

---

# 📁 Test Structure

All tests are currently located inside:

```
monitor/tests.py
```

The test suite is divided into logical test classes:

```
tests.py

├── WebsiteTestCase
│
├── StatusCheckModelTestCase
│
├── WebsiteSecurityTestCase
│
├── AuthenticationTestCase
│
└── WebsiteViewTestCase
```

Each class focuses on a specific part of the application.

---

# ▶️ Running Tests

Run the complete test suite:

```bash
python manage.py test monitor
```

Django will:

1. Create a temporary test database
2. Run all test cases
3. Validate assertions
4. Destroy the test database

Example:

```
Ran 18 tests

OK
```

---

# 🗄️ Model Testing

## WebsiteTestCase

Tests the behavior of the `Website` model.

The test setup creates:

- A test user
- A test website

Example:

```python
self.website = Website.objects.create(
    name="Test Website",
    url="http://testwebsite.com",
    owner=self.user
)
```

---

## Testing Uptime Calculation

PingRadar calculates website uptime based on stored `StatusCheck` records.

Formula:

```
Successful Checks
----------------- × 100
Total Checks
```

---

## Zero Status Checks

Test:

```python
test_uptime_is_none_with_zero_checks
```

Purpose:

Verify that uptime returns `None` when no monitoring data exists.

Expected:

```python
None
```

---

## 100% Uptime

Test:

```python
test_uptime_percentage_with_all_up_checks
```

Scenario:

```
StatusCheck
    |
    +-- UP
    |
    +-- UP
```

Expected result:

```
100%
```

---

## Mixed Uptime Calculation

Test:

```python
test_uptime_percentage_with_mixed_checks
```

Scenario:

```
StatusCheck
    |
    +-- UP
    |
    +-- DOWN
```

Expected result:

```
50%
```

---

## Latest Status Check

Test:

```python
test_latest_check_returns_latest_status_check
```

Purpose:

Verify that:

```python
website.latest_check()
```

returns the most recent monitoring result.

The test creates:

```
check1
check2
check3
```

and verifies:

```
latest_check() == check3
```

---

# 📊 StatusCheck Testing

## StatusCheckModelTestCase

Tests the monitoring result model.

The test verifies that monitoring data is stored correctly.

---

## StatusCheck Creation

Test:

```python
test_status_check_creation
```

Validates:

- Website relationship
- Availability status
- HTTP status code
- Response time

Example:

```python
StatusCheck.objects.create(
    website=self.website,
    is_up=True,
    status_code=200,
    response_time_ms=120
)
```

Expected:

```
Website
    |
    |
StatusCheck

is_up = True
status_code = 200
response_time = 120ms
```

---

# 🔐 Security Testing

## WebsiteSecurityTestCase

Tests ownership-based access control.

PingRadar ensures users can only access their own websites.

---

## Owner Access

Test:

```python
test_owner_can_view_own_website
```

Scenario:

```
User A

    owns

Website A
```

Expected:

```
HTTP 200 OK
```

---

## Unauthorized Access Prevention

Test:

```python
test_user_cannot_view_other_users_website
```

Scenario:

```
User A

tries to access

User B's Website
```

Expected:

```
HTTP 404
```

This prevents users from viewing resources they do not own.

---

# 🔑 Authentication Testing

## AuthenticationTestCase

Tests user authentication functionality.

---

## Signup Page Loading

Test:

```python
test_signup_page_loads
```

Purpose:

Verify that the registration page loads successfully.

Expected:

```
HTTP 200
```

---

## Successful Signup

Test:

```python
test_signup_success
```

Simulates:

```
POST /signup/
```

with:

```python
username
password1
password2
```

Validates:

- User creation
- Successful registration flow
- Redirect response

Expected:

```
HTTP 302
```

and:

```python
User.objects.filter(
    username="newuser"
).exists()
```

returns:

```
True
```

---

# 🌐 View Testing

## WebsiteViewTestCase

Tests user-facing website operations.

The setup creates:

- Test user
- Test website
- Logged-in session

---

# Dashboard Tests

## Login Protection

Test:

```python
test_dashboard_requires_login
```

Purpose:

Ensure anonymous users cannot access the dashboard.

Expected:

```
Anonymous User

        |

Redirect

        |

Login Page
```

---

## Dashboard Loading

Test:

```python
test_dashboard_loads_for_authenticated_user
```

Validates:

- Authenticated users can access dashboard
- User websites appear correctly

Expected:

```
HTTP 200
```

---

## User Website Isolation

Test:

```python
test_dashboard_only_shows_owned_websites
```

Scenario:

```
User A

Website A


User B

Website B
```

Expected:

User A dashboard:

```
Website A ✅

Website B ❌
```

---

# Website Management Tests

## Website Detail Page

Test:

```python
test_website_detail_page_loads
```

Checks:

- Website detail page accessibility
- Correct website information displayed

---

## Adding Website

Test:

```python
test_user_can_add_website
```

Validates:

- Website creation
- Ownership assignment
- URL handling

Example:

Input:

```
newexample.com
```

Application converts:

```
https://newexample.com
```

---

## Invalid URL Handling

Test:

```python
test_invalid_url_is_rejected
```

Scenario:

```
not-a-valid-url
```

Expected:

- Website is not created
- Error message displayed

---

## Duplicate Website Prevention

Test:

```python
test_duplicate_website_is_rejected
```

Validates the database constraint:

```python
unique_website_per_user
```

Scenario:

```
Same User

example.com
example.com
```

Expected:

Duplicate creation rejected.

---

## Website Deletion

Test:

```python
test_user_can_delete_website
```

Validates:

- User can delete owned websites
- Database record is removed

---

## Pause/Resume Monitoring

Test:

```python
test_user_can_toggle_pause_website
```

Validates:

Before:

```
is_paused = False
```

After:

```
is_paused = True
```

---

# 🔄 Continuous Integration

PingRadar uses GitHub Actions to automatically run tests when changes are pushed.

CI workflow:

```text
Developer Push

      |

GitHub Actions

      |

Install Dependencies

      |

Run Django Tests

      |

Report Result
```

This ensures:

- New changes do not break existing functionality
- Tests run automatically
- Code quality remains consistent

---

# 🧠 Testing Philosophy

PingRadar follows behavior-focused testing.

Tests validate what the system should do rather than how the code is internally implemented.

Examples:

Instead of testing:

```
specific function calls
```

Tests verify:

```
User can create a website

User cannot access another user's website

Monitoring results are stored correctly
```

---

# 🚀 Future Testing Improvements

Possible future improvements:

## API Testing

When REST APIs are introduced:

- Endpoint testing
- Authentication token testing
- Response validation

---

## Performance Testing

Future monitoring improvements can include:

- Large-scale website simulations
- Database query benchmarking
- Worker performance testing

---

## Integration Testing

Possible additions:

- Complete monitoring workflow tests
- Worker execution tests
- External service mocking

---

# 📚 Learning Notes

Through testing PingRadar, I learned:

- How Django creates isolated test databases
- How to test database models
- How to simulate user requests
- How authentication testing works
- How authorization prevents security issues
- How automated testing improves software reliability

Testing became an important part of understanding backend engineering and building reliable applications.
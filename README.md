# flask-okta
Redirect login to Okta for Flask

Work in progress.

# /userinfo

Example userinfo from Okta docs:

```javascript
{
    "sub": "00uid4BxXw6I6TV4m0g3", # a unique id, user_id
    "name": "John Doe",
    "nickname": "Jimmy",
    "given_name": "John",
    "middle_name": "James",
    "family_name": "Doe",
    "profile": "https: //example.com/john.doe",
    "zoneinfo": "America/Los_Angeles",
    "locale": "en-US",
    "updated_at": 1311280970,
    "email": "john.doe@example.com",
    "email_verified": true,
    "address" : {
        "street_address": "123 Hollywood Blvd.",
        "locality": "Los Angeles",
        "region": "CA",
        "postal_code": "90210",
        "country": "US"
    },
    "phone_number": "+1 (425) 555-1212"
}
```

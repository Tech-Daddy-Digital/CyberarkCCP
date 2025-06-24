# Call the Web Service using REST {#CalltheWebServiceusingREST}

**In this topic**

- [Call the Web Service using REST](#CalltheWebServiceusingREST)
  - [The GetPassword Web Service](#TheGetPasswordWebService)
    - [URL](#URL)
    - [Resource information](#Resourceinformation)
    - [Query parameters](#Queryparameters)
    - [Result](#Result)
    - [Return codes](#Returncodes)

The **Central Credential Provider** offers the following REST web service:

**GetPassword** – This service enables applications to retrieve passwords from the **Central Credential Provider**. This REST API returns a single password.

## The GetPassword Web Service {#TheGetPasswordWebService}

### URL {#URL}

```text
https://<IIS_Server_Ip>/AIMWebService/api/Accounts?<param1>=<value>&<param2>=<value>& ....
```

> **Note:**
>
> - Make sure there are no spaces in the URL.
> - The following characters are not supported in URL values: `+`, `&`, `%`.

### Resource information {#Resourceinformation}

| HTTP method | HTTP version | Content type     |
| ----------- | ------------ | ---------------- |
| GET         | 1.1          | application/json |

### Query parameters {#Queryparameters}

The following parameters can be specified in the URL to filter the result:

> **Note:**
>
> - Make sure that the name or the value of the account property does not include a special character, such as `;` (semi-colon).
> - The query must contain the **AppID** and at least one other parameter.

| Parameter                                                                                                                  | Purpose                                                                                                                                                                                                                                                                                                                                                | Default | Type    |
| -------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------- | ------- |
| **AppID**                                                                                                                  | Specifies the unique ID of the application issuing the password request.                                                                                                                                                                                                                                                                               |         |         |
| **Required.**                                                                                                              | -                                                                                                                                                                                                                                                                                                                                                      | String  |         |
| **Safe**                                                                                                                   | Specifies the name of the Safe where the password is stored.                                                                                                                                                                                                                                                                                           | -       | String  |
| **Folder**                                                                                                                 | Specifies the name of the folder where the password is stored.                                                                                                                                                                                                                                                                                         |         |         |
| Folders are only supported in **PAM - Self-Hosted**.                                                                       | Root                                                                                                                                                                                                                                                                                                                                                   | String  |         |
| **Object**                                                                                                                 | Specifies the name of the password object to retrieve.                                                                                                                                                                                                                                                                                                 | -       | String  |
| **UserName**                                                                                                               | Defines search criteria according to the UserName account property.                                                                                                                                                                                                                                                                                    | -       | String  |
| **Address**                                                                                                                | Defines search criteria according to the Address account property.                                                                                                                                                                                                                                                                                     | -       | String  |
| **Database**                                                                                                               | Defines search criteria according to the Database account property.                                                                                                                                                                                                                                                                                    | -       | String  |
| **PolicyID**                                                                                                               | Defines the format that will be used in the setPolicyID method.                                                                                                                                                                                                                                                                                        | -       | String  |
| **Reason**                                                                                                                 | The reason for retrieving the password. This reason will be audited in the Credential Provider audit log.                                                                                                                                                                                                                                              | -       | String  |
| **Connection Timeout**                                                                                                     | The number of seconds that the Central Credential Provider will try to retrieve the password.                                                                                                                                                                                                                                                          |         |         |
| The timeout is calculated when the request is sent from the web service to the Vault and returned back to the web service. | 30                                                                                                                                                                                                                                                                                                                                                     | Int     |         |
| **Query**                                                                                                                  | Defines a free query using account properties, including Safe, folder, and object. When this method is specified, all other search criteria (Safe/Folder/Object/UserName/Address/PolicyID/Database) are ignored and only the account properties that are specified in the query are passed to the Central Credential Provider in the password request. | -       | String  |
| **Query Format**                                                                                                           | Defines the query format, which can optionally use regular expressions.                                                                                                                                                                                                                                                                                |         |         |
| Possible values: `Exact`, `Regexp`.                                                                                        | Exact                                                                                                                                                                                                                                                                                                                                                  | String  |         |
| **FailRequestOnPasswordChange**                                                                                            | Whether or not an error will be returned if this web service is called when a password change process is underway.                                                                                                                                                                                                                                     | False   | Boolean |

### Result {#Result}

The following example shows the structure of a result:

```json
{
  "Content": <password>,
  "UserName": <username>,
  "Address": <address>,
  "Database": <Database>,
  "PasswordChangeInProcess": <PasswordChangeInProcess>
}
Status Code: 200
```

> **Note:** Only the currently defined account properties will be returned, so your result may contain different properties to the example.

The following table explains the possible output parameters:

| Properties                  | Purpose                                                                                           | Type    |
| --------------------------- | ------------------------------------------------------------------------------------------------- | ------- |
| **Content**                 | This parameter returns the password content or an empty value if an error occurs.                 | String  |
| **UserName**                | Returns the UserName property of the password, or an empty value if this property does not exist. | String  |
| **Address**                 | Returns the Address property of the password, or an empty value if this property does not exist.  | String  |
| **Database**                | Returns the Database property of the password, or an empty value if this property does not exist. | String  |
| **PasswordChangeInProcess** | Indicates whether or not a password change is in process.                                         | Boolean |

### Return codes {#Returncodes}

For a complete list of return codes, see [Return Codes](/pam-self-hosted/latest/en/content/webservices/implementing%20privileged%20account%20security%20web%20services.htm#Return).

The following error codes may occur:

| Return code           | Code number | Error code | Use case                                                   |
| --------------------- | ----------- | ---------- | ---------------------------------------------------------- |
| Bad Request           | 400         |            |                                                            |
|                       |             | AIMWS030E  | Invalid query format, etc.                                 |
|                       |             | APPAP227E  | 1. Too many objects.                                       |
|                       |             | APPAP228E  | 2. Too many objects.                                       |
|                       |             | APPAP229E  | 3. Too many objects.                                       |
|                       |             | APPAP007E  | Connection to the Vault has failed.                        |
|                       |             | APPAP081E  | Request message content is invalid.                        |
|                       |             | CASVL010E  | Invalid characters in User Name.                           |
|                       |             | AIMWS031E  | Invalid request. The AppID parameter is required.          |
| Forbidden             | 403         |            |                                                            |
|                       |             | APPAP306E  | App failed on authentication check.                        |
|                       |             | APPAP008E  | "ITATS982E User app11 is not defined", etc.                |
| Not Found             | 404         |            |                                                            |
|                       |             | APPAP004E  | Safe not found, etc.                                       |
| Internal Server Error | 500         |            |                                                            |
|                       |             | APPAP282E  | Password [password] is currently being changed by the CPM. |


# API Aggregator

API Aggregator is a service that brings together multiple APIs from different providers into a single, unified interface. This project makes it easy for developers to access various data such as weather, news, GitHub user information, cryptocurrency prices, and currency exchange rates through a single API key.

## Features

- **Unified Access**: One API key to access multiple services.
- **User Management**: User registration and authentication system using JWT.
- **Caching**: Every request is cached to reduce latency and external API usage.
- **Rate Limiting**: Limits the number of requests to prevent abuse.
- **Encryption**: Sensitive data like external API keys are encrypted at rest.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/username/api-aggregator.git
    cd api-aggregator
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # For Linux/macOS
    venv\Scripts\activate  # For Windows
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure environment variables:**
    Create a `.env` file in the root directory and add the required variables. You will need to obtain API keys from each service used:
    -   [OpenWeatherMap](https://openweathermap.org/api)
    -   [NewsAPI](https://newsapi.org/)
    -   [CoinGecko](https://www.coingecko.com/en/api)
    -   [ExchangeRate-API](https://www.exchangerate-api.com/)

    ```env
    SECRET_KEY=your_django_secret_key
    DEBUG=True
    OPENWEATHER_API_KEY=your_key
    NEWSAPI_API_KEY=your_key
    GITHUB_API_KEY=your_key # Optional
    COINGECKO_API_KEY=your_key
    EXCHANGERATE_API_KEY=your_key
    ENCRYPTION_KEY=your_encryption_key # Create a strong random key
    ```

5.  **Run database migrations:**
    ```bash
    python manage.py migrate
    ```

6.  **Setup services (fetches initial data):**
    ```bash
    python manage.py setup_services
    ```

7.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```

## API Documentation

All API endpoints require an `Authorization` header with the API key obtained from the `/api/create-api-key/` endpoint.

**Header Example:**
```
Authorization: Api-Key <YOUR_API_KEY>
```

### User Authentication

These endpoints are used for user management and API key creation.

#### 1. User Registration

-   **Endpoint**: `POST /api/register/`
-   **Description**: Registers a new user.
-   **Request Body**:
    ```json
    {
        "username": "new_user",
        "email": "user@example.com",
        "password": "strong_password"
    }
    ```
-   **Success Response** (201 Created):
    ```json
    {
        "username": "new_user",
        "email": "user@example.com"
    }
    ```

#### 2. Obtain JWT Token

-   **Endpoint**: `POST /api/token/`
-   **Description**: Obtains a JWT (access and refresh) token after registration.
-   **Request Body**:
    ```json
    {
        "username": "new_user",
        "password": "strong_password"
    }
    ```
-   **Success Response** (200 OK):
    ```json
    {
        "access": "access_token",
        "refresh": "refresh_token"
    }
    ```

#### 3. Create API Key

-   **Endpoint**: `POST /api/create-api-key/`
-   **Description**: Creates an API key for authenticating to the aggregator services.
-   **Headers**: Requires a JWT `access` token for Bearer authentication.
    ```
    Authorization: Bearer <ACCESS_TOKEN>
    ```
-   **Success Response** (200 OK):
    ```json
    {
        "user": "new_user",
        "api_key_id": "api_key_id",
        "api_key": "generated_api_key",
        "message": "Save this API key securely!"
    }
    ```

---

### API Services

These endpoints are the core of the aggregator, providing access to various data.

#### 1. Unified Weather

-   **Endpoint**: `GET /api/weather/`
-   **Description**: Gets the current weather data from OpenWeatherMap.
-   **Query Parameters**:
    -   `city` (string, optional, default: `London`): Name of the city.
    -   `country` (string, optional, default: `UK`): 2-letter country code.
-   **Example Request**: `/api/weather/?city=Jakarta&country=ID`

#### 2. Unified News

-   **Endpoint**: `GET /api/news/`
-   **Description**: Gets top headlines from NewsAPI.
-   **Query Parameters**:
    -   `category` (string, optional, default: `general`): News category (e.g., `business`, `technology`).
-   **Example Request**: `/api/news/?category=technology`

#### 3. GitHub User Info

-   **Endpoint**: `GET /api/github/user/`
-   **Description**: Gets a GitHub user's profile information.
-   **Query Parameters**:
    -   `username` (string, **required**): GitHub username.
-   **Example Request**: `/api/github/user/?username=torvalds`

#### 4. Crypto Simple Price

-   **Endpoint**: `GET /api/simple/price/`
-   **Description**: Gets the current price of one or more cryptocurrencies against one or more fiat currencies from CoinGecko.
-   **Query Parameters**:
    -   `ids` (string, **required**): Coin IDs (e.g., `bitcoin`, `ethereum`). Comma-separated for multiple coins.
    -   `vs_currencies` (string, **required**): Comparison currency (e.g., `usd`, `idr`). Comma-separated for multiple currencies.
-   **Example Request**: `/api/simple/price/?ids=bitcoin&vs_currencies=usd`

#### 5. Crypto Coin Detail

-   **Endpoint**: `GET /api/coins/`
-   **Description**: Gets detailed information for a single cryptocurrency from CoinGecko.
-   **Query Parameters**:
    -   `id` (string, **required**): Coin ID (e.g., `bitcoin`).
-   **Example Request**: `/api/coins/?id=ethereum`

#### 6. Coin Market Chart

-   **Endpoint**: `GET /api/coins/market_chart/`
-   **Description**: Gets historical market data for a chart from CoinGecko.
-   **Query Parameters**:
    -   `id` (string, **required**): Coin ID.
    -   `vs_currency` (string, **required**): Comparison currency (e.g., `usd`).
    -   `days` (integer, **required**): Number of days for historical data.
-   **Example Request**: `/api/coins/market_chart/?id=bitcoin&vs_currency=usd&days=7`

#### 7. Coin Price History

-   **Endpoint**: `GET /api/coins/history/`
-   **Description**: Gets historical price data for a coin on a specific date from CoinGecko.
-   **Query Parameters**:
    -   `id` (string, **required**): Coin ID.
    -   `date` (string, **required**): Date in `dd-mm-yyyy` format.
-   **Example Request**: `/api/coins/history/?id=bitcoin&date=30-12-2017`

#### 8. Search (CoinGecko)

-   **Endpoint**: `GET /api/search/`
-   **Description**: Searches for coins, exchanges, and categories on CoinGecko.
-   **Query Parameters**:
    -   `query` (string, **required**): Search keyword.
-   **Example Request**: `/api/search/?query=solana`

#### 9. Search Trending (CoinGecko)

-   **Endpoint**: `GET /api/search/trending/`
-   **Description**: Gets the trending coins on CoinGecko.
-   **Example Request**: `/api/search/trending/`

#### 10. Currency Exchange Rates

-   **Endpoint**: `GET /api/exchanges-rate/`
-   **Description**: Gets the latest exchange rates based on a base currency from ExchangeRate-API.
-   **Query Parameters**:
    -   `currency` (string, **required**): Base currency code (e.g., `USD`).
-   **Example Request**: `/api/exchanges-rate/?currency=USD`

#### 11. Currency Conversion

-   **Endpoint**: `GET /api/pair/`
-   **Description**: Converts an amount from one currency to another.
-   **Query Parameters**:
    -   `from` (string, **required**): Source currency code.
    -   `to` (string, **required**): Target currency code.
    -   `amount` (float, optional): The amount to convert.
-   **Example Request**: `/api/pair/?from=USD&to=IDR&amount=100`

## Running Tests

To ensure all functionality is working correctly, run the tests:

```bash
python manage.py test
```

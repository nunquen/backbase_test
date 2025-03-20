# Implement REST APIs
✅ Migration
    - Create currencies
        - EUR, CHF, USD and GBP
        - Have USD as base currency

✅ Currency rates list
    - Description: Service to retrieve a List of currency rates for a specific time period
    - Expected response: a time series list of rate values for each available Currency
    - Parameters:
        - source_currency
        - date_from
        - date_to

    - NOTES:
        - Step1: look for stored time series between dates
        - Step2: if any date is missing, then fetch remotly data only for those missing days
            - symbols: have all currencies as a Set, remove the base and have the rest splitted by "," with no whit spaces.
        - Step3: save new items if any
        - Step4: retrieve requested items

- Convert amount
    - Description: Service that calculates (latest) amount in a currency exchanged into a different currency (currency converter)
    - Expected response: An object containing at least the rate value between source and exchange currencies.
    - Parameters:
        - source_currency
        - exchanged_currency
        - amount

    - NOTES:
        - Step1: look for convert rate in ddbb
            - Step 1.1: 
                - Improvement: define an expiration time of X seconds (5 minutes)
                - Convert rate will be remotely retrieved after expiration time has been reached only for the current date!
        - Step2: if there's no convert rate request from adapter
            - convert will implement CurrencyBeacon endpooint as is
            - Retrieve remote data 
            - store it in the data base

✅ CRUD of currencies
    - apply crud for currencies

- PRIORITY
    - create a new provider entity that will hold
        - Provider name - unique field
        - provider key
        - is_enabled: True/False
        - priority: only positive numbers - unique field
    
    - Logic:
        - App will get the enabled provider with the lowest priority
    -> Improvement
        - Link CurrencyExchangeRate with provider for future audit purpose (in case of discovering bad data)

- ADMIN
    - Implement CONVERTER view: it could be possible to set a source currency and multiple target currencies.

- ASYNC
    - Implement an asynchronous method to load this historical data as quickly and efficiently as possible, minimizing resource consumption.
    - What do you think is a better option: concurrency or parallelism?
    -> Approach: go month by month and retrieve each base currency in parallel

- TEST
    - Provide a mechanism to ingest real-ish exchange rate data for testing purposes.
    - Define tests

- API Version
    - MyCurrency API could have different API versions or scopes 
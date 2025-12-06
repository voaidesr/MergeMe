# Flight Rotables Optimisation

The link to the repo containing the challenge can be found [here](https://github.com/pradu3/HackitAll2025).

## Setup

```
python -m venv .venv
source .venv/bin/activate
```
Add all requirements to [requirements.txt](./requirements.txt). To install them:

```
pip install --upgrade pip
pip install -r requirements.txt
```

You need to create locally and `.env` file in order to be able to send requests.

```
cp .env.example .env
```

Inside the `.env` file, set the desired API key and the url base.

## Structure

- `src/main.py` - I envision this to be the entry point, the script in which we call the other modules and implement the final product. I want us to work as modularly as possible so that we can turn this into an api more easily later.
- `src/utils` - Module with data transfer objects necessary for the request
- `src/api_client` - Module that implements the `ApiClient` class with all the required methods.

## Statistics

The histogram of the time it takes to process a kit at each airport:

![](./statistics/imgs/processing_times.png)

On the provided that, we can see the utilisation faction of kits (passenger=pax/kit space per plane)

![](./statistics/imgs/flight_utilization_hist.png)

The average and median values of needed kits can be found [here](./statistics/flight_kits_vs_capacity_summary.csv)



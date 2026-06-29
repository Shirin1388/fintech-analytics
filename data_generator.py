from faker import Faker
import pandas as pd
import random
from datetime import datetime

fake = Faker()
random.seed(42)

def generate_transactions(n=50000):
    customers = [fake.uuid4() for _ in range(500)]
    customer_home_countries = {c: fake.country_code() for c in customers}
    merchants = ["Amazon", "Uber", "Shell", "Coles", "CommBank ATM",
                 "PayPal", "Crypto Exchange X", "Casino Online"]

    rows = []
    for _ in range(n):
        amount = round(random.gauss(100, 80), 2)
        amount = max(1.0, amount)
        if random.random() < 0.05:
            amount = round(random.uniform(9000, 50000), 2)

        customer_id = random.choice(customers)
        # only 10% of transactions are from a different country than the customer's home country
        if random.random() < 0.1:
            country = fake.country_code()
        else:
            country = customer_home_countries[customer_id]

        hour = random.choices(
            range(24),
            weights=[1,1,1,1,1,1,3,5,8,10,10,10,8,10,10,10,8,6,5,4,3,2,2,1]
        )[0]
        ts = fake.date_time_between("-1y", "now")
        ts = ts.replace(hour=hour)

        rows.append({
            "transaction_id": fake.uuid4(),
            "customer_id": customer_id,
            "merchant_name": random.choice(merchants),
            "amount_usd": amount,
            "transaction_ts": ts.isoformat(),
            "country": country,
            "channel": random.choices(["online", "pos", "atm", "wire"],
                                       weights=[40, 30, 20, 10])[0],
            "status": random.choices(["completed", "failed", "pending"],
                                      weights=[85, 10, 5])[0]
        })

    return pd.DataFrame(rows)

df = generate_transactions()
df.to_csv("/home/shirin/fintech-analytics/raw_transactions.csv", index=False)
print(f"Generated {len(df)} rows")
print(df.head())
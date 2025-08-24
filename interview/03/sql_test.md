## Question
The key metric, UPA (Units Per Address), is calculated based on daily delivery history per worker and address. It is derived using the formula: units divided by stops (number of addresses) delivered by a single worker. If a worker revisits the same address within 10 minutes, it is counted as a single stop. However, if the revisit occurs after 10 minutes, the stop count is incremented by one. Based on this logic, a query is written to calculate UPA.


## Schema
```sql
CREATE TABLE upa_base
(
    workday               INT,
    address_hash_content  VARCHAR(255),
    worker_id             INT,
    units                 INT,
    delivery_datetime     VARCHAR(14) -- yyyymmddHHmiss
);
```


## Sample data
```sql
INSERT INTO upa_base (workday, address_hash_content, worker_id, units, delivery_datetime) VALUES
(20220108, '-676509909026244000', 1052659, 1, '20220108100630'),
(20220108, '-676509909026244000', 1052659, 2, '20220108110632'),
(20220108, '-676509909026244000', 1052659, 1, '20220108120638'),
(20220108, '-676509909026244000', 1052659, 1, '20220108130836'),
(20220108, '-676509909026244000', 1052659, 1, '20220108130836'),
(20220108, '-672062329566743000', 1365573, 1, '20220108130836'),
(20220108, '-672062329566743000', 1365573, 1, '20220108160326'),
(20220108, '-670630966482500000', 1677016, 1, '20220108121843'),
(20220108, '-670630966482500000', 1677016, 1, '20220108180456'),
(20220108, '-676509909025182000', 1852659, 1, '20220108102222'),
(20220108, '-676509909025182000', 1852659, 1, '20220108102522');
```

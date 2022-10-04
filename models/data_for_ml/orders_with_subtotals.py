#imports
import pyspark.pandas as ps


def model(dbt, session):

    # get upstream data
    orders = dbt.ref("orders").pandas_api()
    products = dbt.ref("stg_products").pandas_api()
    order_items = dbt.ref("stg_order_items").pandas_api()

    # get the subtotal for each product_id for each order_id
    order_item_product_subtotals = order_items.merge(products, on="product_id").pivot(
        index="order_id", columns="product_id", values="product_price"
    )

    # rename the product_id columns to include "subtotal_"
    renames = {col: f"subtotal_{col}" for col in order_item_product_subtotals.columns}
    order_item_product_subtotals = order_item_product_subtotals.rename(columns=renames)

    # fill NaNs with 0s
    order_item_product_subtotals = order_item_product_subtotals.fillna(0)

    # merge with the existing orders mart
    orders_with_subtotals = orders.merge(
        order_item_product_subtotals, left_on="order_id", right_index=True
    )  # .set_index("order_id")

    return orders_with_subtotals

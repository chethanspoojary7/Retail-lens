REQUIRED_COLUMNS = ["InvoiceNo", "StockCode", "Description", "Quantity", "InvoiceDate", "UnitPrice", "CustomerID", "Country"]
REFERENCE_DATE = "2011-12-10"
FEATURE_COLUMNS = ["recency", "frequency", "monetary", "avg_order_value", "unique_products"]
# Log-transformed before scaling (all are right-skewed in retail data).
LOG_COLUMNS = ["frequency", "monetary", "avg_order_value", "unique_products"]
RANDOM_STATE = 42

# app.py
import pandas as pd

from shiny import reactive
from shiny.express import input, render, ui
from shiny.types import FileInfo

# Upload a dataset
ui.page_opts(title = "Upload a Table and Supply Missing Values")
ui.help_text(ui.markdown("Consider using this [example file](sales.csv) to try the app below."))
ui.input_file("file", "Choose CSV File", accept=[".csv"], multiple=False)

# Global state to hold the original data
original_data = reactive.Value(pd.DataFrame())

@reactive.calc
def parsed_data():
    file: list[FileInfo] | None = input.file()
    if file is None:
        return pd.DataFrame()
    df = pd.read_csv(
        file[0]["datapath"], 
        keep_default_na=False, 
        na_values=[]
    )
    original_data.set(df)
    return df

# Filter to rows of interest
ui.input_text("value", "Missing value symbol", value="NaN")
ui.input_checkbox("show_all", "Show all data", value=False)


@reactive.calc
def filtered_data():
    df = parsed_data()
    if df.empty:
        return pd.DataFrame(columns=["No data available"])  # Return empty DataFrame if no data

    # Show all data without filtering if "show_all" is checked
    if input.show_all():
        return df
     # Filter rows containing the missing value symbol
    missing_value_symbol = input.value()
    mask = df.apply(lambda row: row.astype(str).eq(missing_value_symbol), axis=1).any(axis=1)
    filtered_df = df[mask]
    return filtered_df


# Display data in editable table
@render.data_frame
def data():
    return render.DataGrid(filtered_data(), editable=True)

# Add custom edit behavior
@data.set_patch_fn
def upgrade_patch(*, patch,):
    df = original_data.get()
    row_index, col_index = patch["row_index"], patch["column_index"]
    orig_value = df.iat[row_index, col_index]

    # Allow editing only if the cell matches the missing value symbol or show_all is checked
    if orig_value == input.value() or input.show_all():
        df.iat[row_index, col_index] = patch["value"]
        original_data.set(df)  # Update the original data
        return patch["value"]
    else:
        ui.notification_show(
            f"You can only edit cells with the missing value symbol '{input.value()}'.",
            type="error",
        )
        return orig_value

# Download the finished data
@render.download(label="Download", filename="updated-data.csv")
def download():
    yield data.data_view().to_csv(index=False)
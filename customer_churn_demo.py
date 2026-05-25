# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "altair>=5.5.0",
#     "marimo>=0.23.3",
#     "numpy>=2.0.0",
#     "pandas>=2.2.0",
# ]
# ///

import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium")


@app.cell
def _():
    import altair as alt
    import marimo as mo
    import numpy as np
    import pandas as pd

    return alt, mo, np, pd


@app.cell
def _(mo):
    mo.md("""
    # Reaktiv kundeanalyse 2

    Endre kontrollene under og se hvordan data, KPI-er og grafen oppdateres automatisk.
    Testcasen bruker syntetiske kundedata, så den kan kjøres helt lokalt.
    """)
    return


@app.cell
def _(mo):
    customer_count = mo.ui.slider(
        start=100,
        stop=2_000,
        step=50,
        value=600,
        label="Antall kunder",
    )
    churn_pressure = mo.ui.slider(
        start=0,
        stop=100,
        step=5,
        value=45,
        label="Markeds-/konkurransepress",
    )
    segment_filter = mo.ui.dropdown(
        options=["Alle", "Privat", "SMB", "Enterprise"],
        value="Alle",
        label="Segment",
    )
    discount = mo.ui.slider(
        start=0,
        stop=30,
        step=1,
        value=8,
        label="Rabatt i behold-kampanje (%)",
    )

    mo.vstack(
        [
            mo.hstack([customer_count, churn_pressure], justify="start"),
            mo.hstack([segment_filter, discount], justify="start"),
        ]
    )
    return churn_pressure, customer_count, discount, segment_filter


@app.cell
def _(churn_pressure, customer_count, np, pd):
    rng = np.random.default_rng(42)
    n = customer_count.value

    segments = rng.choice(
        ["Privat", "SMB", "Enterprise"],
        size=n,
        p=[0.62, 0.28, 0.10],
    )
    monthly_revenue = np.select(
        [segments == "Privat", segments == "SMB", segments == "Enterprise"],
        [
            rng.normal(329, 70, n),
            rng.normal(1_450, 330, n),
            rng.normal(8_500, 1_900, n),
        ],
    ).clip(99)
    support_cases = rng.poisson(
        np.select(
            [segments == "Privat", segments == "SMB", segments == "Enterprise"],
            [0.8, 1.6, 2.7],
        )
    )
    tenure_months = rng.gamma(shape=3.2, scale=8.5, size=n).clip(1, 96)
    usage_score = rng.beta(4, 2, size=n) * 100

    pressure = churn_pressure.value / 100
    segment_risk = np.select(
        [segments == "Privat", segments == "SMB", segments == "Enterprise"],
        [0.09, 0.07, 0.045],
    )
    churn_risk = (
        segment_risk
        + pressure * 0.18
        + support_cases * 0.018
        - tenure_months * 0.0014
        - usage_score * 0.0012
    ).clip(0.01, 0.75)

    customers = pd.DataFrame(
        {
            "segment": segments,
            "monthly_revenue": monthly_revenue.round(0),
            "support_cases": support_cases,
            "tenure_months": tenure_months.round(1),
            "usage_score": usage_score.round(1),
            "churn_risk": churn_risk.round(3),
            "expected_loss": (monthly_revenue * churn_risk).round(0),
        }
    )
    customers["risk_bucket"] = pd.cut(
        customers["churn_risk"],
        bins=[0, 0.12, 0.25, 1],
        labels=["Lav", "Middels", "Høy"],
        include_lowest=True,
    )
    return (customers,)


@app.cell
def _(customers, segment_filter):
    filtered = (
        customers
        if segment_filter.value == "Alle"
        else customers[customers["segment"] == segment_filter.value]
    )
    return (filtered,)


@app.cell
def _(discount, filtered, mo):
    avg_risk = filtered["churn_risk"].mean()
    expected_loss = filtered["expected_loss"].sum()
    campaign_effect = min(0.45, discount.value * 0.012)
    retained_value = expected_loss * campaign_effect

    mo.hstack(
        [
            mo.stat(
                label="Kunder i utvalg",
                value=f"{len(filtered):,}".replace(",", " "),
            ),
            mo.stat(label="Snittrisiko", value=f"{avg_risk:.1%}"),
            mo.stat(
                label="Forventet månedstap",
                value=f"{expected_loss:,.0f} kr".replace(",", " "),
            ),
            mo.stat(
                label="Estimert reddet verdi",
                value=f"{retained_value:,.0f} kr".replace(",", " "),
            ),
        ],
        justify="start",
    )
    return campaign_effect, expected_loss, retained_value


@app.cell
def _(alt, filtered):
    chart_data = (
        filtered.groupby(["segment", "risk_bucket"], observed=True)
        .agg(
            customers=("segment", "size"),
            expected_loss=("expected_loss", "sum"),
            avg_revenue=("monthly_revenue", "mean"),
        )
        .reset_index()
    )

    risk_chart = (
        alt.Chart(chart_data)
        .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
        .encode(
            x=alt.X("segment:N", title="Segment"),
            y=alt.Y("customers:Q", title="Antall kunder"),
            color=alt.Color(
                "risk_bucket:N",
                title="Risiko",
                scale=alt.Scale(
                    domain=["Lav", "Middels", "Høy"],
                    range=["#2f855a", "#d69e2e", "#c53030"],
                ),
            ),
            tooltip=[
                "segment:N",
                "risk_bucket:N",
                "customers:Q",
                alt.Tooltip("expected_loss:Q", title="Forventet tap", format=",.0f"),
                alt.Tooltip("avg_revenue:Q", title="Snittinntekt", format=",.0f"),
            ],
        )
        .properties(height=320)
    )
    risk_chart
    return


@app.cell
def _(mo):
    mo.md("""
    ## Kundene med høyest forventet tap
    """)
    return


@app.cell
def _(filtered, mo):
    top_customers = (
        filtered.sort_values("expected_loss", ascending=False)
        .head(12)
        .reset_index(drop=True)
    )
    mo.ui.table(top_customers, page_size=12)
    return


@app.cell
def _(campaign_effect, discount, expected_loss, mo, retained_value):
    mo.md(
        f"""
        ## Simulering

        Med **{discount.value}% rabatt** antar modellen at kampanjen reduserer risikoen
        med **{campaign_effect:.1%}** for kundene i utvalget.

        Det gir en estimert reddet månedsverdi på **{retained_value:,.0f} kr**
        av et forventet tap på **{expected_loss:,.0f} kr**.
        """.replace(
            ",", " "
        )
    )
    return


@app.cell
def rabatt_sensitivitet(alt, discount, expected_loss, filtered, mo, pd):

    scenario_discounts = pd.DataFrame({"discount_pct": range(0, 31, 2)})
    scenario_discounts["risk_reduction"] = scenario_discounts["discount_pct"].mul(0.012).clip(upper=0.45)
    high_risk = filtered[filtered["risk_bucket"] == "Høy"]
    monthly_campaign_base = high_risk["monthly_revenue"].sum()
    scenario_discounts["retained_value"] = expected_loss * scenario_discounts["risk_reduction"]
    scenario_discounts["campaign_cost"] = monthly_campaign_base * scenario_discounts["discount_pct"] / 100
    scenario_discounts["net_effect"] = scenario_discounts["retained_value"] - scenario_discounts["campaign_cost"]

    current_discount_row = scenario_discounts.loc[
        scenario_discounts["discount_pct"].sub(discount.value).abs().idxmin()
    ]

    sensitivity_chart = (
        alt.Chart(scenario_discounts.melt("discount_pct", value_vars=["retained_value", "campaign_cost", "net_effect"]))
        .mark_line(point=True)
        .encode(
            x=alt.X("discount_pct:Q", title="Rabatt (%)"),
            y=alt.Y("value:Q", title="Kroner per måned"),
            color=alt.Color(
                "variable:N",
                title="Metrikk",
                scale=alt.Scale(
                    domain=["retained_value", "campaign_cost", "net_effect"],
                    range=["#2b6cb0", "#dd6b20", "#2f855a"],
                ),
            ),
            tooltip=[
                alt.Tooltip("discount_pct:Q", title="Rabatt"),
                alt.Tooltip("variable:N", title="Metrikk"),
                alt.Tooltip("value:Q", title="Verdi", format=",.0f"),
            ],
        )
        .properties(height=280)
    )

    mo.vstack(
        [
            mo.md(
                f"""
                ## Rabatt-sensitivitet

                Ved valgt rabatt på **{discount.value}%** er estimert nettoeffekt
                **{current_discount_row['net_effect']:,.0f} kr per måned** etter kampanjekostnad.
                """.replace(",", " ")
            ),
            sensitivity_chart,
        ]
    )

    return


if __name__ == "__main__":
    app.run()

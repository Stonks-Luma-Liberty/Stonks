import tempfile
from io import BufferedReader, BytesIO

from discord import Interaction, File
from discord.enums import ButtonStyle
from discord.ui import Button
from inflection import humanize
from plotly.graph_objects import Candlestick, Figure
from plotly.io import to_image

from api.coingecko import CoinGecko


class ChartButton(Button):
    def __init__(self, label: str, symbol: str, days: str):
        super(ChartButton, self).__init__(label=label, style=ButtonStyle.primary)
        self.coin_gecko = CoinGecko()
        self.token_ids = label
        self.symbol = symbol
        self.days = days

    async def callback(self, interaction: Interaction) -> None:
        """
        Responds with appropriate token chart data
        :param interaction: Discord bot interaction
        """
        market = await self.coin_gecko.coin_market_lookup(
            ids=self.token_ids, time_frame=self.days, base_coin="usd"
        )
        fig = Figure(
            data=[
                Candlestick(
                    x=market.Date,
                    open=market.Open,
                    high=market.High,
                    low=market.Low,
                    close=market.Close,
                ),
            ]
        )
        fig.update_layout(
            title=f"Candlestick graph for {humanize(self.token_ids)} ({self.symbol})",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            xaxis_rangeslider_visible=False,
        )

        fig.update_yaxes(tickprefix="$")

        await interaction.response.send_message(
            file=File(
                BufferedReader(
                    BytesIO(to_image(fig, format="png", engine="kaleido"))  # type: ignore
                ),
                filename=f"{tempfile.NamedTemporaryFile()}.png",
            )
        )

# Batter Scouting Scorecard
[Baseball Batter Scouting Tool](https://wisd2024-batter-scouting-tool.streamlit.app/)

Batting is one of the most complicated movements in sports. It requires full-body coordination, excellent timing, patience, and precision. Assessing a batter's quality and potential can be highly variable and subjective. In this project, I have created four metrics to evaluate different parts of a batter's swing and provided a tool that allows a scout to fine-tune the target ranges for these metrics to generate a final overall grade for the batter. Details on the [metrics](docs/Metric%20Details.md) and [tool](docs/Tool%20Details.md) can be found in the [docs folder](docs/).

## Summary
This project focused on the idea of scouting players based on their batting skills. These skills are often summarized by on base percentage, slugging, or batting average. Bat tracking data provides the opportunity to analyze specific components of a players swing instead of the aggregate outcomes. This level of detail allows clubs to identify the components of a swing that are the most important for their teams. The important components could be the parts that the manager believes are most valuable, the parts the batting coach believes are innate talent, or the processes that correlates with scoring runs. 

Four new metrics were developed that isolate a portion of the baseball swing. The swing similarity tracks a player's consistency in mechanics. The pitch hunting metric evaluates the batter's patience. The contact location metric measures the timing. Finally, the tracking angle builds an additional layer onto attack angle to provide a single measure of the pitch and swing angles.

A scouting tool allows users to tweak the grading ranges and set custom priorities. The customization allows users to identify their most important metrics and to set custom rankings. The tool also provides users with visuals of the metrics for a selected batter. This will accelerate the evaluation and comparison of batters.

## Future Work
1. Metrics Correlation - In the future, these new metrics could be included in correlation analysis or used to model game outcomes. Analyzing a full season of data would provide sufficient data to determine how well these new metrics correlate with different performance metrics. These analysis would allow for better default setting for the metrics grading or suggestions for priorities or weighting when ranking batters.
1. Limitation Reduction - Each of the metrics comes with it's own set of limitations. Some of the limitations can be mitigated with additional time or additional data. Specifically, with additional data, the swing similarity analysis could tease apart details like pitch type or pitch location.
1. Tool Extention - The tool was designed with a scout in mind, but these swing metrics can be valuable for pitchers prepping for their next series, or for batter reflecting on their performance. The tool could be adjusted for each of these use cases. For the scout, an additional option to review two or more batters at the same time would also be a valuable addition.

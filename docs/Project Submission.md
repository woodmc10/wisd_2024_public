# Project Submission Sections
## Introduction
Batting is one of the most complicated movements in sports. It requires full-body coordination, excellent timing, patience, and precision. Assessing a batter's quality and potential can be highly variable and subjective. In this project, I have created four metrics to evaluate different parts of a batter's swing and provided a tool that allows a scout to fine-tune the target ranges for these metrics to generate a final overall grade for the batter. The GitHub repo contains additional details on the metrics and tool in the docs folder. (https://github.com/woodmc10/wisd_2024_public/tree/main/docs)

## Purpose & Motivation
This project focused on scouting players based on their batting skills. These skills are often summarized by on-base percentage, slugging, or batting average. Bat tracking data allows one to analyze specific components of a player's swing instead of the aggregate outcomes. This level of detail will enable clubs to identify the most essential elements of a swing for their teams. These components could be the parts that the manager believes are most valuable, the parts the batting coach believes are innate talent, or the processes that correlate with scoring runs. 

## Solution
Four new metrics were developed that isolate a portion of the baseball swing. The swing similarity tracks a player's consistency in mechanics. The pitch-hunting metric evaluates the batter's patience. The contact location metric measures the timing. Finally, the tracking angle builds an additional layer onto the attack angle to provide a single measure of the pitch and swing angles. More details about each of the metrics can be found here: https://github.com/woodmc10/wisd_2024_public/blob/main/docs/Metric%20Details.md. 

A scouting tool (https://wisd2024-batter-scouting-tool.streamlit.app/) allows users to tweak the grading ranges and set custom priorities. This customization will enable users to identify their most important metrics and to set custom rankings. The tool also provides users with visuals of the metrics for a selected batter. These visuals will accelerate the evaluation and comparison of batters. The similairty score is not included in the scouting tool because it needs to pull the complete tracking data to generate scores and plots. Specific instructions for navigating the scouting tool can be found here: https://github.com/woodmc10/wisd_2024_public/blob/main/docs/Tool%20Details.md.

## How/When to Use Application
This tool was designed with a scout in mind. The potential scenario where this tool would be most helpful would be after an entire minor league season when a scout wants to identify the best players to acquire. After processing the swings and loading the summary details (which is not a part of this public project), the scout would be able to impart their experience and knowledge into the grading and evaluation of each batter. The tool would then rank the players based on the scout's input, and the scout would be able to visually verify the ranking by reviewing the metric plots. 

## Difficulties and Challenges Faced
Working with the bat tracking data was exciting and challenging in many ways—the complexity of the data required time to peel apart. The data structure became clearer after plotting and animating some examples of swings, but keeping the pos_0, pos_1, and pos_2 axes straight required constant vigilance throughout the project. The next challenge was breaking the swing into smaller components that a single metric could summarize. There is an incredible amount of content on the internet about the best way to swing a baseball bat, and finding a few that aligned with our perspective was challenging. 

The data presented its own challenges. Slight variations or issues with the data often required adjusting the processing to gracefully capture differences. Comprehensive error handling would be incredibly valuable for processing this type of complex data, but it was not part of the scope of this project. Instead, each type of error was addressed as it was encountered. 

Finally, creating the app required addressing nuances of visual spacing, stateful management of variables, and user experience. The code for generating polished, thoughtful plots and deploying the app was the most time-consuming to write. 

## Next Steps
* Metrics Correlation - These new metrics could be included in correlation analysis or used to model game outcomes. Analyzing an entire season of data would provide sufficient data to determine how well these new metrics correlate with different performance metrics. This analysis would allow for better default settings for the metrics grading or suggestions for priorities or weighting when ranking batters.
* Limitation Reduction - Each of the metrics has its limitations. Some of the limitations can be mitigated with additional time or data. Specifically, with further data, the swing similarity analysis could tease apart details, like pitch type or pitch location.
* Tool Extention - The tool was designed with a scout in mind, but these swing metrics can be valuable for pitchers prepping for their next series, or for a batter reflecting on their performance. The tool could be adjusted for each of these use cases. For the scout, an additional option to review two or more batters simultaneously would also be a valuable addition.
* Composite Score - The tool currently allows the user to rank the players by setting the priority of the different metrics. Additional value could be provided by determining a composite score for each player that would offer better rankings. The composite score could be a weighting applied to each metric to generate a final score more nuanced than the graded rankings.

## GitHub Link
https://github.com/woodmc10/wisd_2024_public/

## Website Link
https://wisd2024-batter-scouting-tool.streamlit.app/


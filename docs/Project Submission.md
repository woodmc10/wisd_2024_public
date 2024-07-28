# Project Submission Sections
## Introduction
Batting is one of the most complicated movements in sports. It requires full-body coordination, excellent timing, patience, and precision. Assessing a batter's quality and potential can be highly variable and subjective. In this project, I have created four metrics to evaluate different parts of a batter's swing and provided a tool that allows a scout to fine-tune the target ranges for these metrics to generate a final overall grade for the batter. Details on the metrics and tool can be found in the [docs folder](https://github.com/woodmc10/wisd_2024_public/tree/main/docs).

## Purpose & Motivation
This project focused on the idea of scouting players based on their batting skills. These skills are often summarized by on base percentage, slugging, or batting average. Bat tracking data provides the opportunity to analyze specific components of a players swing instead of the aggregate outcomes. This level of detail allows clubs to identify the components of a swing that are the most important for their teams. The important components could be the parts that the manager believes are most valuable, the parts the batting coach believes are innate talent, or the processes that correlates with scoring runs. 

## Solution
Four new metrics were developed that isolate a portion of the baseball swing. The swing similarity tracks a player's consistency in mechanics. The pitch hunting metric evaluates the batter's patience. The contact location metric measures the timing. Finally, the tracking angle builds an additional layer onto attack angle to provide a single measure of the pitch and swing angles. More details about each of the metrics can be found here https://github.com/woodmc10/wisd_2024_public/blob/main/docs/Metric%20Details.md 

A scouting tool (https://wisd2024-batter-scouting-tool.streamlit.app/) allows users to tweak the grading ranges and set custom priorities. The customization allows users to identify their most important metrics and to set custom rankings. The tool also provides users with visuals of the metrics for a selected batter. This will accelerate the evaluation and comparison of batters. The similairty score is not included in the scouting tool due to it's need to pull the full tracking data to generate scores and plots. Specific instructions for navigating the scouting tool can be found here https://github.com/woodmc10/wisd_2024_public/blob/main/docs/Tool%20Details.md

## How/When to Use Application
This tool was designed with a scout in mind. The potential scenario where this tool would be most useful would be after a full minor league season when a scout was trying to identify the best players to aquire. After processesing the swings and loading the summary details (with is not a part of this public project) the scout would be able to impart their experience and knowledge into the grading and evaluation of each batter. The tool would then rank the players based on the scout's input and the scout would be able to visually verify the ranking by reviewing the metric plots. 

## Difficulties and Challenges Faced
Working with the bat tracking data was exciting and challenging in many ways. The complexity of the data required time to peel apart. After plotting and animating some examples of swings it became more clear how things were structured. Even so, keeping the pos_0, pos_1, and pos_2 axes straight required constant vigilance through out the project. The next challenge was breaking the swing into smaller components that could be summarized by a single metric. There is an incredible amout of content on the interent about the best way to swing a baseball bat, and finding a few that aligned with our perspective was difficult. 

In addition to these larger difficulties, the data itself provided a number of challenges. Small variations or issues with the data often required adjusting the processing to gracefully capture differences. Comprehensive error handling would be incredibly valuable for processing this type of complex data, but was not part of the scope of this project. Instead each type of error was addressed as it was encountered. 

Finally, creating the app required addressing nuances of visual spacing, stateful management of variables, and user experience. The code for generating polished, thoughtful plots and deploying the app were the most time consuming to write. 

## Next Steps
* Metrics Correlation - In the future, these new metrics could be included in correlation analysis or used to model game outcomes. Analyzing a full season of data would provide sufficient data to determine how well these new metrics correlate with different performance metrics. These analysis would allow for better default setting for the metrics grading or suggestions for priorities or weighting when ranking batters.
* Limitation Reduction - Each of the metrics comes with it's own set of limitations. Some of the limitations can be mitigated with additional time or additional data. Specifically, with additional data, the swing similarity analysis could tease apart details like pitch type or pitch location.
* Tool Extention - The tool was designed with a scout in mind, but these swing metrics can be valuable for pitchers prepping for their next series, or for batter reflecting on their performance. The tool could be adjusted for each of these use cases. For the scout, an additional option to review two or more batters at the same time would also be a valuable addition.
* Composite Score - The tool currently allows the user to rank the players by setting the priority of the different metrics. Additional value could be provided by determining a composite score for each player that would provide better rankings. The composite score could be a weighting applied to each of the metrics to generate a final score with more nuance than the graded rankings.

## GitHub Link
https://github.com/woodmc10/wisd_2024_public/

## Website Link
https://wisd2024-batter-scouting-tool.streamlit.app/


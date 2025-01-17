## Customization Tool
The swing scouting [dashboard](https://wisd2024-swing-metric-dashboard.streamlit.app/) allows scouts to customize the grades for each of the metrics. They can set the acceptable quality contact locations, pitch hunting radius, tracking angle ranges, and swing similairty percent good swings. In addition to updating the grades, the user can change the ranking of the batters by selecting the prefered priority for each of the metrics. The tool will provide a list of all the batters with a sufficient number of swings and show the grades for each of the metrics. The user can then select a batter to view the visuals for each of their metrics. 

### Navigation
The tool is navigated with radio buttons in the sidebar. The first tab is the Custom Grading page. When switching to the Scorecard tab the metric priority and swing count widgets will become available in the side bar. Similarly, the batter selection dropdown becomes avaiable in the side bar on the Batter Plots tab.

<img src="../images/tool/navigation.png" height="250">

### Set Custom Grading Ranges
The first section in the tool allows the user to set the custom grading ranges. 

**Contact Location:**
The contact location grading ranges are defaulted to the ranges correlating with home runs, line drives, and grounders.[^3] The sliders can be moved to set the target locations. Each swing is given a grade based on the range it falls into. The final grade of the batter is average of all the swing scores. 

<img src="../images/tool/contact_location_widget.png" height="500">

**Pitch Hunting Radius:**
Similar to the contact location grading ranges, the hunting ranges are set using a slider and assigned a score based on the assigned grade. The final hunting grade is also the average of all the swing scores. When setting the sliders, the Grade A values should be the lowest and each subsequent grade should be higher than the previous to avoid errors.

<img src="../images/tool/hunting_widget.png" height="500">

**Tracking Angle Ranges:**
The tracking angle tool allows the user to select from a set of preset angle widths. These widths determine the range above and below the pitch that is assigned a particular score. For example, if Grade A is set to 2.5 and Grade B is set to 5 then swings within 2.5 degrees of the pitch angle (above or below) will be awarded 4 points, and swings between 2.5 and 7.5 degrees of the pitch angle (above or below) will be assigned 3 points. As with the contact location and pitch hunting, the average of all the swing scores gives the final tracking angle grade. There is no risk of errors when setting these values, but the user should consider that smaller values will leave more swings outside of the graded ranges, resulting in no points awarded for those swings and lower overall grades.

<img src="../images/tool/tracking_angle_widget.png" height="500">


**Swing Similarity:**
The swing similarity grade is calculated differently than all of the other metrics. The score is determined by the percent of the batter's swings that are within two standard deviations of the mean. The swing similarity grade can be customized by setting the perecent ranges that result in each grade. 

<img src="../images/tool/swing_similarity_widget.png" height="400">

**Sliders:**
The sliders will update to keep the ranges connected, but the user will need to ensure ranges are small enough to keep all four grades - sliders should not be set with one range encompasing another range to avoid errors.

**Grades:**
Contact location, pitch hunting, and tracking angle metrics assign a score for each swing based on the following grades:
- Grade A = 4 points
- Grade B = 3 points
- Grade C = 2 points
- Grade D = 1 point

### Set Grading Priorities and Minimum Swing Count
After setting all of the grading values, the user is provided the opportunity to change the priority order of the metrics for ranking the batters and to restrict the batter list to only batters with a minimum number of swings. The order of the metrics should reflect the most important values to the user. A scout that wants patient players who only swing at pitches they can hit should prioritize pitch hunting, while a scout that wants players with home run swings should prioritize contact location. The swing count minimum allows the user to set a base of how many swings each batter must have. Larger numbers of swings will reduce the variability in scores. 

<img src="../images/tool/priority_widget.png" height="450">

### Batter Scorecard
The ranked batter scorecard displays the list of batters and their scores on each metrics. The order of the batters is determined by the priorities set by the user, and the order of columns will reflect the user selected metric priorities. For example, in the image below the user is most interested in the hunting and contact location grades.

<img src="../images/tool/batter_scorecard.png" height="500">

### Batter Selection and Visualization
Finally, in the Batter Plots tab, the user selects a batter from the ordered list to display the metrics visuals. This allows the user to verify the performance of the selected batter. The visuals will be sorted in the order of the user selected metric priorities.


## Footnotes
[^3]: Hammit, Brock. (2019, February 9). Using Point of Impact to Measure Timing. https://medium.com/@hammit21/using-point-of-impact-to-measure-timing-b79ca6958221
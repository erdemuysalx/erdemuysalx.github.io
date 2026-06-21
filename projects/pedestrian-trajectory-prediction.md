# Behavior-Aware Pedestrian Trajectory Prediction
2023-02-11
GitHub: 
Paper: 
Image: /public/images/pedestrian-trajectory-prediction.gif
Sprite: /public/images/me-pixel-mobile_robot.png
Order: 3

Abstract: Navigating through urban environments is a safety-critical task in autonomous driving due to the existing vulnerable road users. In this report, we study the problem of predicting pedestrian trajectory from an onboard camera perspective. Most of the current works are flawed at capturing the dynamics of pedestrian motions. We propose a Behavior-Aware Transformer (BAT) which leverages a transformer network and behavioral features to model the highly dynamic behavior of pedestrians in urban traffic. Our method includes modifications and extensions upon a baseline method. BAT method fuses the past observed trajectory, ego-vehicle’s speed and behavioral features, pose, and body orientation, using the intermediate fusion stage. The resulting mixed representation from the intermediate fusion stage is passed to the decoder where it is jointly decoded with optical flow representation from the center and target areas which are incorporated to compensate for the ego-motion of the vehicle. Our Behavior-Aware Transformer is evaluated on the PIE dataset and showed both quantitatively and qualitatively that utilizing behavioral features enables our method to capture the highly dynamic behaviors of pedestrians.
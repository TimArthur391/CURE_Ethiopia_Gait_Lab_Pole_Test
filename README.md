# CURE_Ethiopia_Gait_Lab_Pole_Test
 As part of the CMAS requirements for a gait lab, a 'pole test' must be completed everyday that the lab is used for patient data collection. 
 
 The test detailed here uses: (1) a rigid pole with a marker pair placed near the top, and a marker pair placed near the bottom; (2) whilst Vicon Nexus is recording, the pole should be pressed into all 4 corners of each force plate, with pressure being applied by pivoting the pole in a circular motion; (3) the trial is reconstructed and 'Pole_Test_Vx.py' is run; (4) the midpoint of each pair is found and used to construct a line between these 2 points within the local coordinate system; (5) the x and y coordinates where this line intersects the floor (where z = 0 in the local coordinate system), is compared to the x and y coordinates output from the force plates centre of pressure measurement; (6) the root mean squared error between these coordinates is calculated, and if it is less than 20mm, then it is deemed a pass.

 The jupyter notebook that was used to analyse, write and debug this code has been included as it explains the code step by step.

 
 For more information on the pole test see the following references:
 
Baker R. The “Poker” test: a spot check to confirm the accuracy of kinetic gait data. Gait Posture. 1997;5(2):177-8.

Collins SH, Adamczyk PG, Ferris DP, Kuo AD. A simple method for calibrating force plates and force treadmills using an instrumented pole. Gait Posture. 2009 Jan;29(1):59-64.

Della Croce U, Cappozzo A. A spot check for estimating stereophotogrammetric errors. Med Biol Eng Comput. 2000 May;38(3):260-6.

Holden JP, Selbie WS, Stanhope SJ. A proposed test to support the clinical movement analysis laboratory accreditation process. Gait Posture. 2003 Jun;17(3):205-13.

Lewis A, Stewart C, Postans N, Trevelyan J. Development of an instrumented pole test for use as a gait laboratory quality check. Gait Posture. 2007 Jul;26(2):317-22.

Rabuffetti M, Ferrarin M, Benvenuti F. Spot check of the calibrated force platform location. Med Biol Eng Comput. 2001 Nov;39(6):638-43. 

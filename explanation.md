1. we link the alerts based on their

   - service topology
   - temporal proximity

2. for every such link we calculate the confidence interval of that
   alert being in this group based on the historical data

3. finds the root cause using graph traversal.

4. send the group to appropriate teams, also collect feedback about the prediction.
   based on feedback we can change the state of the alert dependancy.

1. we link the alerts based on their

   - service topology
   - temporal proximity

2. for every such link we calculate the confidence interval of that
   alert being in this group based on the historical data

3. finds the root cause using graph traversal.

4. send the group to appropriate teams, also collect feedback about the prediction.
   based on feedback we can change the state of the alert dependancy.

5. What happens when a new link appears

   - due to change in how thinks work a new kind of relation occours.
   - due to a new service deployed and new link popsup.

   1. the link will be having less strength will be not considerd. and delt seperately
      over time the probability of the link to appear increases and then eventually the
      state gets stabilized, also this will take some time to have some strength.
      to reduce the time taken for this system the support people can give some feedback about the incident.

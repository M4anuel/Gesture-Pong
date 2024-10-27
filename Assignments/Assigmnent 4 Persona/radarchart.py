import matplotlib.pyplot as plt
import numpy as np

# Values for Tom's Big Five personality traits
labels = ['Aufgeschlossenheit', 'Gewissenhaftigkeit', 'Extraversion', 'Verträglichkeit', 'Neurotizismus']
# labels = ["A", "G", "E", "V", "N"]
# labels = ["","","","",""]
values = [6, 8, 5, 7, 4]
markers = list(range(1,11,2))

# Number of variables
num_vars = len(labels)

# Compute angle for each axis
angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()

# Complete the loop by connecting the first and last
values += values[:1]
angles += angles[:1]

# Plot
fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))

ax.fill(angles, values, color='blue', alpha=0.25)
ax.plot(angles, values, color='blue', linewidth=2)

# Labels for each axis
ax.set_yticklabels(markers)
ax.set_xticks(angles[:-1])
ax.set_xticklabels(labels, fontsize=15)  
plt.yticks(markers, fontsize=15)
ax.grid(True)
# Adjust tick label positions ------------------------------------
X_VERTICAL_TICK_PADDING = 20
X_HORIZONTAL_TICK_PADDING = 20
XTICKS = ax.xaxis.get_major_ticks()
for tick in XTICKS[0::2]:
    tick.set_pad(X_VERTICAL_TICK_PADDING)
    
for tick in XTICKS[1::2]:
    tick.set_pad(X_HORIZONTAL_TICK_PADDING)

# Title plt.title('Tom Müller\'s Big Five Personality Traits', size=20, color='blue', y=1.1)
plt.savefig('Big5.png', transparent=True)
# Show plot
plt.show()
import matplotlib.pyplot as plt

# Interests data
aspects = ['Saving Costs', 'Environmental Awareness', 'Energy Efficiency', 'Family Sustainability', 'Smart Home Automation']
levels = [16, 10, 16, 12, 16]

# Plot
plt.barh(aspects, levels, color='skyblue')
plt.xlabel('Interest Level')
plt.title('Tom Müller\'s Interest Levels')
plt.show()

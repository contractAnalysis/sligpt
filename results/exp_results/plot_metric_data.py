#================
# July 16, 2024
# the code to present the data for Sligpt paper

import matplotlib.pyplot as plt
import numpy as np

# Data
tools = ['Slither', 'GPT-4o', 'Sligpt']
categories = ['Precision', 'Recall', 'Accuracy', 'F1 Score']
data = [
    [0.88 , 0.84, 0.76 , 0.86 ],   # Data for Tool 1
    [0.72, 0.90, 0.67, 0.80 ],   # Data for Tool 2
    [0.91 , 0.96 , 0.88 , 0.93 ]    # Data for Tool 3
]


# Number of categories
n_categories = len(categories)
n_tools = len(tools)

# Setting the positions and width for the bars
bar_width = 0.2
index = np.arange(n_categories)

# Plotting the bars
fig, ax = plt.subplots(figsize=(12, 4))
for i in range(n_tools):
    bars=ax.bar(index + i * bar_width, data[i], bar_width, label=tools[i])
    # Adding text labels on top of the bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2.0, height, f'{height:.2f}',
                ha='center', va='bottom')

# Adding labels
ax.set_xlabel('Metrics')
ax.set_ylabel('Metric Value')
# ax.set_title('')
ax.set_xticks(index + bar_width / 2 * (n_tools - 1))
ax.set_xticklabels(categories)
ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

# Adjusting layout to make room for the legend
plt.tight_layout(rect=[0, 0, 0.85, 1])

# Displaying the chart
plt.show()


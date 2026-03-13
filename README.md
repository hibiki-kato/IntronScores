# IntronScores

This repository stores and visualizes the sequence evaluation scores and Sensitivity/Precision metrics for the IntronModel project.

## Specifications

- **Automatic Labeling and Plotting** 
  When a score file (`.txt`) is placed under `data/{species}/`, the filename (excluding the extension) is automatically read and used as the legend label in the generated plot.
- **Automatic Updates (GitHub Actions)**
  Whenever a new score file is pushed to the `main` (or `master`) branch, or daily at 13:00 UTC (8:00 AM EST), a GitHub Actions workflow runs automatically. It regenerates the plot images (`{Species}_snpr.png`) for each species, and then commits and pushes the updated images back to the repository.

## Google Colab / Jupyter Notebook

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/hibiki-kato/IntronScores/blob/main/notebook/plot_scores.ipynb)

You can easily run the plotting scripts in the cloud using Google Colab. By clicking the badge above, the notebook will open in your browser, automatically clone this repository (including the data files), and generate the plots.

## Manual Plotting & Interactive Mode

If you want to manually verify the plots locally or customize the display, you can use `plot.sh`.

```bash
# Regenerate all images locally using the default non-interactive mode
./plot.sh

# Regenerate images for specific species only (multiple species allowed)
./plot.sh --species "Mmus, Dmel"

# Check the plotting results using the interactive GUI mode
./plot.sh --interactive on
```

**About Interactive Mode:**
When executed with `--interactive on`, the plots will open in GUI windows. 
You can **click on the Legend** in the opened plot window to dynamically toggle the visibility (show/hide) of specific lines/points.

*Note: In interactive mode, the script runs background processes to launch multiple windows simultaneously and will not finish executing until all plot windows are closed.*

---

## ⚠️ Caution: Git Conflicts

Because GitHub Actions automatically regenerates and pushes images back to the repository, taking these updates into account locally is critical.

**Before you `push` your local changes, ALWAYS run `git pull` to fetch the latest images and scripts.** 
If you fail to `pull` first, you will very likely encounter a Git conflict due to the automatically updated `*_snpr.png` images that already exist on the remote branch.

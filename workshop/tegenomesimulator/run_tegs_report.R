args <- commandArgs(trailingOnly = TRUE)
genome_file <- normalizePath(args[1])
repeat_fasta <- normalizePath(args[2])
repeat_gff   <- normalizePath(args[3])
project_prefix <- args[4]
out_dir <- args[5]

# Get --file argument safely and extract the path
args_full <- commandArgs(trailingOnly = FALSE)
file_arg <- sub("--file=", "", args_full[grep("--file=", args_full)])

if (length(file_arg) == 0) {
  stop("Could not determine script location. Are you running with Rscript?")
}

this_script <- normalizePath(file_arg)
this_dir <- dirname(this_script)

# Ensure output directory exists
if (!dir.exists(out_dir)) {
  dir.create(out_dir, recursive = TRUE)
}

# Ensure the directory to the script was extracted correctly
if (!dir.exists(this_dir)) {
  stop("Script directory does not exist: ", this_dir)
}

# Render Rmd file
rmarkdown::render(paste0(this_dir, "/summarise_demo_m0.Rmd"),
                  params = list(
                      genome_fasta = genome_file,
                      repeat_fasta = repeat_fasta,
                      repeat_gff = repeat_gff,
                      project_prefix = project_prefix,
                      out_dir = out_dir,
                      script_dir = this_dir
                  ),
                  output_file = paste0("tegenomesimulator_report_", project_prefix, ".html"),
                  output_dir = out_dir,
                  knit_root_dir = this_dir
                  )

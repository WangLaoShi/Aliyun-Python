import os

# Specify the folder path containing the Markdown files
folder_path = "./"

# Specify the output file path
output_file = "阿里云天池Python训练营.md"

# Get a list of Markdown files in the specified folder
# markdown_files = [file for file in os.listdir(folder_path) if file.endswith(".md")]
markdown_files = ['阿里云天池Python训练营-Part1.md','阿里云天池Python训练营-Part2.md',
                  '阿里云天池Python训练营-Part3.md','阿里云天池Python训练营-Part4.md']
# Open the output file in write mode
with open(output_file, "w") as outfile:
    # Iterate over each Markdown file
    for file in markdown_files:
        # Open the Markdown file in read mode
        with open(os.path.join(folder_path, file), "r") as infile:
            # Write the filename to the output file
            # outfile.write(f"# {file}\n\n")

            # Write the contents of the Markdown file to the output file
            outfile.write(infile.read())

            # Add a line break between files
            outfile.write("\n\n---\n\n")

print("Concatenation complete. Output file:", output_file)
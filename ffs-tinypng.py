import sys
import tinify
import dotenv
import os
from pathlib import Path
import asyncio

# what types of files are we going to optimize
extensions = ['*.png', '*.jpeg', '*.jpg']

# max file size in megabytes
MAX_FILE_SIZE = 2  # 2mb

# max attempts to make to compress the file
MAX_COMPRESSING_ATTEMPTS = 3

# load env
dotenv.load_dotenv()

# tiny_png auth
tinify.key = os.getenv("TINYFY_API_KEY")


# pass image file path. tinfy will replace the current file with the resized one
async def optimize(image_path: str):
    try:
        source = tinify.from_file(image_path)
        source.to_file(image_path)

    except Exception as e:
        print(f"\nError occurred while processing file {image_path}. Error log: {str(e)}")


# look up the specified path and count, find and allocate files. optionally also only get files with a certain size
async def look_up(path, min_size=None):
    # initialize the counter at 0
    total_count = 0
    # create an empty list initialized at 0
    extension_count = [0] * len(extensions)
    # extensions string
    found_extensions = ""
    # all the found files (their paths)
    files = []

    # loop through all files of given extensions
    for i, extension in enumerate(extensions):
        for file_path in Path(path).rglob(extension):

            # if min size isnt provided return all of them
            # otherwise return the conditional files
            if min_size is None or (min_size is not None and Path(file_path).stat().st_size > min_size):
                total_count += 1
                extension_count[i] += 1
                files.append(file_path)

    # populate the extensions string
    for i, extension in enumerate(extensions):
        found_extensions += f"{extension}: {extension_count[i]} | "

    return total_count, found_extensions, files


async def main():
    # request path from user
    path = input("Specify the folder path: ")

    # check path availability
    if not os.path.exists(path):
        print("Specified path does not exist! please try again...\n")
        await main()  # restart over if path is not found

    # get total files found, extended files and file paths in specified path
    print(f"Looking up '{path}' for {extensions}...")
    total_count, found_extensions, files = await look_up(path)
    print(f"Look up complete! Found a total of {total_count} files. | {found_extensions[:-2].replace('*.', '')}")

    # start the compression
    print(f"\nStarting compression..")
    for i, file_path in enumerate(files):
        sys.stdout.write(f"\rCompressed {i} of {total_count} images | {round(i / total_count * 100, 2)}% | Compressing file: {file_path}")
        await optimize(file_path)

    sys.stdout.write(f"\rCompressed {total_count} of {total_count} images | 100%")
    sys.stdout.flush()
    # compression finished! Now check if there are still any files over 2mb

    # loop through the amount of times we can attempt to compress
    for j in range(MAX_COMPRESSING_ATTEMPTS + 1):
        # get all files above MAX_FILE_SIZE
        total_count, found_extensions, files = await look_up(path, MAX_FILE_SIZE*1000000)

        # do we have at least one file to compress?
        if total_count > 0:

            if j == 0:
                print(f"\nAdditional compression required: {total_count} files found above {MAX_FILE_SIZE}M limit!")

            # do we still have compressing attempts?
            if j < MAX_COMPRESSING_ATTEMPTS:

                # alright lets start compressing..
                print(f"\nFound {total_count} more files to compress.. compressing (Attempt {j+1} of {MAX_COMPRESSING_ATTEMPTS})")
                for i, file_path in enumerate(files):
                    sys.stdout.write(f"\rCompressed {i} of {total_count} images | {round(i / total_count * 100, 2)}% | Compressing file: {file_path}")
                    await optimize(file_path)
                sys.stdout.write(f"\rCompressed {total_count} of {total_count} images | 100%")
                sys.stdout.flush()
            else:

                # more files to compress were found but we have no more compressing attempts left :/
                print(f"\nAttention! {total_count} more files to compress found but out of attempts ({MAX_COMPRESSING_ATTEMPTS})\n")
                print(f"Following files were compressed yet their size is greater than {MAX_FILE_SIZE}M:\n")
                for file_path in files:
                    print(f"{file_path}\n")
        else:

            # if all files were compressed successfully before reaching max attempts then just exit the loop
            break

    # all done:)
    print("\nCompression completed successfully!")

if __name__ == "__main__":
    # run main async
    asyncio.get_event_loop().run_until_complete(main())

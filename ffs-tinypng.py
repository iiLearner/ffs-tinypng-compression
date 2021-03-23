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


async def optimize(image_path: str):
    source = tinify.from_file(image_path)
    source.to_file(image_path)


async def lookUp(path, min_size=None):
    totalCount = 0
    extensionCount = [0] * len(extensions)
    found_extensions = ""
    files = []
    for i, extension in enumerate(extensions):
        for file_path in Path(path).rglob(extension):
            if min_size is None:
                totalCount += 1
                extensionCount[i] += 1
                files.append(file_path)
            else:
                if Path(file_path).stat().st_size > min_size:
                    totalCount += 1
                    extensionCount[i] += 1
                    files.append(file_path)

    for i, extension in enumerate(extensions):
        found_extensions += f"{extension}: {extensionCount[i]} | "

    return totalCount, found_extensions, files


async def main():
    # request path from user
    path = input("Specify the folder path: ")

    # check path availability
    if not os.path.exists(path):
        print("Specified path does not exist! please try again...\n")
        await main()  # restart over if path is not found

    # get total files found, extended files and file paths in specified path
    print(f"Looking up '{path}' for {extensions}...")
    totalCount, found_extensions, files = await lookUp(path)
    print(f"Look up complete! Found a total of {totalCount} files. | {found_extensions[:-2].replace('*.', '')}")

    # start the compression
    print(f"\nStarting compression..")
    for i, file_path in enumerate(files):
        sys.stdout.write(f"\rCompressed {i} of {totalCount} images | {round(i / totalCount * 100, 2)}%")
        await optimize(file_path)

    sys.stdout.write(f"\rCompressed {totalCount} of {totalCount} images | 100%")
    sys.stdout.flush()
    # compression finished! Now check if there are still any files over 2mb

    # loop through the amount of times we can attempt to compress
    for j in range(MAX_COMPRESSING_ATTEMPTS + 1):

        # get all files above MAX_FILE_SIZE
        totalCount, found_extensions, files = await lookUp(path, MAX_FILE_SIZE*1000000)

        # do we have at least one file to compress?
        if totalCount > 0:

            if j == 0:
                print(f"\nAdditional compression required: {totalCount} files found above {MAX_FILE_SIZE}M limit!")

            # do we still have compressing attempts?
            if j < MAX_COMPRESSING_ATTEMPTS:

                # alright lets start compressing..
                print(f"\nFound {totalCount} more files to compress.. compressing (Attempt {j+1} of {MAX_COMPRESSING_ATTEMPTS})")
                for i, file_path in enumerate(files):
                    sys.stdout.write(f"\rCompressed {i} of {totalCount} images | {round(i / totalCount * 100, 2)}%")
                    await optimize(file_path)
                sys.stdout.write(f"\rCompressed {totalCount} of {totalCount} images | 100%")
                sys.stdout.flush()
            else:

                # more files to compress were found but we have no more compressing attempts left :/
                print(f"\nAttention! {totalCount} more files to compress found but out of attempts ({MAX_COMPRESSING_ATTEMPTS})\n")
        else:

            # if all files were compressed successfully before reaching max attempts then just exit the loop
            break

    # all done:)
    print("\nCompression completed successfully!")

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())

import logging
import os
import asyncio
import time
from typing import Optional
import requests

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def humanbytes(size: Optional[int]) -> str:
    """
    Formats a byte size into a human-readable string.

    Args:
        size (int): The size in bytes.

    Returns:
        str: A human-readable string representing the size.
    """
    if not size or size <=0:
        return "0 B"
    
    power = int(math.floor(math.log(size, 1024)))
    
    Dic_powerN = {0: '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    
    size_formatted = round(size / 1024 ** power, 2)
    
    return f"{size_formatted} {Dic_powerN[power]}B"

def DetectFileSize(url: str) -> int:
    """
    Retrieves the content length (file size) from a URL's response headers.
    Args:
        url (str): The URL of the file.
    Returns:
        int: The total size of the file if the file size can be retrieved, otherwise 0.
    """
    try:
        r = requests.get(url, allow_redirects=True, stream=True)
        r.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        total_size = int(r.headers.get("content-length", 0))
        logger.debug(f"Detected file size: {total_size} bytes for URL: {url}")
        return total_size
    except requests.exceptions.RequestException as e:
        logger.error(f"Error while detecting file size for URL {url}: {e}")
        return 0
    except Exception as e:
       logger.error(f"An unexpected error occurred: {e}")
       return 0


async def DownLoadFile(
    url: str,
    file_name: str,
    chunk_size: int,
    client,
    ud_type: str,
    message_id: int,
    chat_id: int
) -> str:
    """
    Downloads a file from a URL with progress updates for a Telegram bot.

    Args:
        url (str): The URL of the file to download.
        file_name (str): The local path to save the downloaded file.
        chunk_size (int): The size of the download chunks.
        client: A Telegram bot client object (likely from a library like Pyrogram).
        ud_type (str): A string indicating "upload" or "download" (for progress updates).
        message_id (int): The Telegram message ID to update with progress.
        chat_id (int): The Telegram chat ID to update the message in.
    Returns:
        str: The file name if the download was successful, otherwise the `file_name`
    """
    if os.path.exists(file_name):
        os.remove(file_name)
        logger.debug(f"Removed existing file: {file_name}")
    
    if not url:
      logger.info("No URL to download")
      return file_name
    
    try:
        logger.debug(f"Start downloading file from URL: {url}")
        r = requests.get(url, allow_redirects=True, stream=True)
        r.raise_for_status()
        total_size = int(r.headers.get("content-length", 0))
        downloaded_size = 0
        start_time = time.time()
        last_update = start_time
        with open(file_name, 'wb') as fd:
          for chunk in r.iter_content(chunk_size=chunk_size):
              if chunk:
                  fd.write(chunk)
                  downloaded_size += len(chunk)
              now = time.time()
              diff = now - last_update
              if client is not None and (diff > 1 or downloaded_size == total_size):
                 percentage = downloaded_size/total_size *100 if total_size else 0
                 try:
                  await client.edit_message_text(
                      chat_id,
                      message_id,
                      text=f"{ud_type}: {humanbytes(downloaded_size)} of {humanbytes(total_size)} ({percentage:.2f}%)"
                  )
                  last_update = now
                 except Exception as e:
                    logger.error(f"Error while updating Telegram message: {e}")

        logger.info(f"Finished downloading file from URL: {url} to {file_name}")
        return file_name

    except requests.exceptions.RequestException as e:
        logger.error(f"Error during download from URL {url}: {e}")
        return file_name
    except Exception as e:
        logger.error(f"An unexpected error occurred during download: {e}")
        return file_name
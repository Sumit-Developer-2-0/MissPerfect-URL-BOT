import logging
import math
import time
import asyncio
from typing import Optional
from config import Config
# the Strings used for this "thing"
from translation import Translation


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def progress_for_pyrogram(
    current: int,
    total: int,
    ud_type: str,
    message,
    start: float
):
    """
    Updates a Telegram message with a progress bar during file transfers.

    Args:
        current (int): The current amount of data transferred.
        total (int): The total amount of data to be transferred.
        ud_type (str): A string to indicate if it is an upload or download progress.
        message: The pyrogram message object to edit.
        start (float): The start time of the transfer.
    """
    
    last_message_content = ""
    
    while current < total:
        now = time.time()
        diff = now - start
        
        percentage = current * 100 / total
        speed = current / diff if diff > 0 else 0
        elapsed_time = round(diff) * 1000
        time_to_completion = round((total - current) / speed) * 1000 if speed > 0 else 0
        estimated_total_time = elapsed_time + time_to_completion

        elapsed_time_str = TimeFormatter(milliseconds=elapsed_time)
        estimated_total_time_str = TimeFormatter(milliseconds=estimated_total_time)

        progress = "[{0}{1}] \nP: {2}%\n".format(
            ''.join(["█" for _ in range(math.floor(percentage / 5))]),
            ''.join(["░" for _ in range(20 - math.floor(percentage / 5))]),
            round(percentage, 2))
        
        tmp = progress + "{0} of {1}\nSpeed: {2}/s\nETA: {3}\n".format(
            humanbytes(current),
            humanbytes(total),
            humanbytes(speed),
            estimated_total_time_str
        )
        
        try:
            if tmp != last_message_content:
              await message.edit(
                text=f"{ud_type}\n {tmp}"
              )
              last_message_content = tmp
            await asyncio.sleep(10) # Update message every 10 seconds
        except Exception as e:
          logger.error(f"Error updating message progress for {ud_type}: {e}")


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
    
    power = math.floor(math.log(size, 1024))
    
    Dic_powerN = {0: '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    
    size_formatted = round(size / 1024 ** power, 2)
    
    return f"{size_formatted} {Dic_powerN[power]}B"


def TimeFormatter(milliseconds: int) -> str:
    """Formats milliseconds into a human-readable time string.
    Args:
        milliseconds (int): The time in milliseconds.

    Returns:
        str: A human-readable string representing the time.
    """
    if not milliseconds:
      return ""
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    time_parts = []
    if days:
        time_parts.append(f"{days}d")
    if hours:
        time_parts.append(f"{hours}h")
    if minutes:
        time_parts.append(f"{minutes}m")
    if seconds:
      time_parts.append(f"{seconds}s")
    if milliseconds:
      time_parts.append(f"{milliseconds}ms")

    return ", ".join(time_parts)
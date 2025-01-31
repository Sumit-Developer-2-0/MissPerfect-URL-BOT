import logging
import asyncio
import os
import time
from typing import Optional, List
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def place_water_mark(
    input_file: str,
    output_file: str,
    water_mark_file: str,
    watermark_scale: float = 0.5,
    watermark_position: str = "bottom-right"
) -> Optional[str]:
    """Adds a watermark to a video file.

    Args:
        input_file (str): Path to the input video file.
        output_file (str): Path to the output watermarked video file.
        water_mark_file (str): Path to the watermark image file.
        watermark_scale (float): The scale factor to resize the watermark. Default 0.5.
        watermark_position (str): The position of the watermark ("top-left", "top-right",
            "bottom-left", "bottom-right"). Default is "bottom-right".

    Returns:
        Optional[str]: The path to the watermarked output if successful, None otherwise.
    """
    watermarked_file = output_file + ".watermark.png"
    try:
      if not os.path.lexists(input_file):
        logger.error(f"Input file not found: {input_file}")
        return None
      if not os.path.lexists(water_mark_file):
        logger.error(f"Watermark file not found: {water_mark_file}")
        return None

      metadata = extractMetadata(createParser(input_file))
      if not metadata or not metadata.has("width"):
          logger.error(f"Failed to extract video width from {input_file}")
          return None
      width = metadata.get("width")

      # Create command to shrink watermark
      shrink_watermark_command = [
          "ffmpeg",
          "-i", water_mark_file,
          "-y -v quiet",
          "-vf", f"scale={int(width*watermark_scale)}:-1",
          watermarked_file
      ]
      logger.debug(f"Executing command to scale watermark: {' '.join(shrink_watermark_command)}")
      process = await asyncio.create_subprocess_exec(
          *shrink_watermark_command,
          stdout=asyncio.subprocess.PIPE,
          stderr=asyncio.subprocess.PIPE,
      )
      stdout, stderr = await process.communicate()
      if process.returncode != 0:
          logger.error(f"Failed to scale watermark: {stderr.decode().strip()}")
          return None

      # Calculate watermark position
      positions = {
        "top-left": "0:0",
        "top-right": "(main_w-overlay_w):0",
        "bottom-left": "0:(main_h-overlay_h)",
        "bottom-right": "(main_w-overlay_w):(main_h-overlay_h)",
    }
      overlay_position = positions.get(watermark_position, "(main_w-overlay_w):(main_h-overlay_h)")

      # Create command to overlay watermark onto the video
      overlay_command = [
          "ffmpeg",
          "-i", input_file,
          "-i", watermarked_file,
          "-filter_complex", f"overlay={overlay_position}",
          output_file
      ]
      logger.debug(f"Executing command to apply watermark: {' '.join(overlay_command)}")
      process = await asyncio.create_subprocess_exec(
          *overlay_command,
          stdout=asyncio.subprocess.PIPE,
          stderr=asyncio.subprocess.PIPE,
      )
      stdout, stderr = await process.communicate()

      if process.returncode != 0:
          logger.error(f"Failed to apply watermark to video: {stderr.decode().strip()}")
          return None
      logger.info(f"Successfully watermarked {input_file}")
      os.remove(watermarked_file) # cleanup the intermediate file
      return output_file
    except Exception as e:
      logger.error(f"An exception occurred during place_water_mark: {e}")
      return None


async def take_screen_shot(video_file: str, output_directory: str, ttl: int) -> Optional[str]:
    """Takes a screenshot from a specific time within a video.
    Args:
      video_file (str): Path to the video file.
      output_directory (str): Path to the directory for saving the screenshot.
      ttl (int): Time-to-live(time to take screen shot)
    Returns:
      Optional[str]: The path to the screenshot if successful, None otherwise.
    """
    try:
      if not os.path.lexists(video_file):
          logger.error(f"Video file not found: {video_file}")
          return None
      if not os.path.exists(output_directory):
          os.makedirs(output_directory)
          logger.info(f"Created output directory: {output_directory}")

      output_file_name = os.path.join(output_directory, f"{time.time()}.jpg")
      
      command = [
          "ffmpeg",
          "-ss", str(ttl),
          "-i", video_file,
          "-vframes", "1",
          output_file_name
      ]
      logger.debug(f"Executing command: {' '.join(command)}")
      process = await asyncio.create_subprocess_exec(
          *command,
          stdout=asyncio.subprocess.PIPE,
          stderr=asyncio.subprocess.PIPE,
      )
      stdout, stderr = await process.communicate()
      if process.returncode != 0:
          logger.error(f"Failed to take screenshot of video {video_file}: {stderr.decode().strip()}")
          return None

      logger.info(f"Screenshot taken from {video_file} and saved to {output_file_name}")
      return output_file_name
    except Exception as e:
      logger.error(f"An exception occurred during take_screen_shot: {e}")
      return None

async def cult_small_video(
    video_file: str,
    output_directory: str,
    start_time: str,
    end_time: str
) -> Optional[str]:
    """Cuts a segment of a video based on start and end times.

    Args:
        video_file (str): Path to the input video file.
        output_directory (str): Path to the directory to save the cut video.
        start_time (str): The start time for the cut (format: "HH:MM:SS.ms").
        end_time (str): The end time for the cut (format: "HH:MM:SS.ms").

    Returns:
        Optional[str]: The path to the cut video if successful, None otherwise.
    """
    try:
        if not os.path.lexists(video_file):
           logger.error(f"Video file not found: {video_file}")
           return None
        if not os.path.exists(output_directory):
           os.makedirs(output_directory)
           logger.info(f"Created output directory: {output_directory}")

        output_file_name = os.path.join(output_directory, f"{round(time.time())}.mp4")

        command = [
            "ffmpeg",
            "-i", video_file,
            "-ss", start_time,
            "-to", end_time,
            "-async", "1",
            "-strict", "-2",
            output_file_name
        ]
        logger.debug(f"Executing command to cut video: {' '.join(command)}")
        process = await asyncio.create_subprocess_exec(
           *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
           logger.error(f"Failed to cut video {video_file}: {stderr.decode().strip()}")
           return None

        logger.info(f"Cutted video {video_file} and saved to {output_file_name}")
        return output_file_name
    except Exception as e:
        logger.error(f"An exception occurred during cult_small_video: {e}")
        return None



async def generate_screen_shots(
    video_file: str,
    output_directory: str,
    is_watermarkable: bool,
    wf: Optional[str],
    min_duration: int,
    no_of_photos: int
) -> Optional[List[str]]:
    """Generates multiple screenshots from a video.
    Args:
      video_file (str): Path to the input video file.
      output_directory (str): Path to the directory for saving the generated images.
      is_watermarkable (bool): If true, watermarks are added to images
      wf (str): Path to the water mark file.
      min_duration (int): Videos shorter than this will not get screen shots
      no_of_photos (int): How many screenshots should be generated
    Returns:
      Optional[List[str]]: A list of paths of the screenshots if successful, None otherwise.
    """
    try:
        if not os.path.exists(output_directory):
           os.makedirs(output_directory)
           logger.info(f"Created output directory: {output_directory}")

        if not os.path.lexists(video_file):
           logger.error(f"Video file not found: {video_file}")
           return None

        metadata = extractMetadata(createParser(video_file))
        duration = 0
        if metadata is not None and metadata.has("duration"):
            duration = metadata.get('duration').seconds

        if duration > min_duration:
            images = []
            ttl_step = duration // no_of_photos
            current_ttl = ttl_step
            for _ in range(no_of_photos):
                ss_img = await take_screen_shot(video_file, output_directory, current_ttl)
                if ss_img:
                    if is_watermarkable and wf:
                        watermarked_image = await place_water_mark(ss_img, os.path.join(output_directory, f"{time.time()}.jpg"), wf)
                        if watermarked_image:
                          images.append(watermarked_image)
                        else:
                          logger.error(f"Failed to watermark: {ss_img}, skipping screenshot.")
                          os.remove(ss_img)
                    else:
                        images.append(ss_img)
                else:
                  logger.error(f"Failed to get screenshot skipping it.")
                current_ttl += ttl_step
            return images
        else:
          logger.info(f"Video {video_file} is shorter than {min_duration}")
          return None
    except Exception as e:
      logger.error(f"An exception occurred during generate_screen_shots: {e}")
      return None
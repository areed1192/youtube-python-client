import json
import pathlib
import win32com.client as win32

from win32com.client import CDispatch

from pprint import pprint
from typing import List
from typing import Dict
from collections import namedtuple


class AdobeIllustrator():

    def __init__(self, file_name: str = None) -> None:
        """Initializes the `Win32Adobe` client.

        ## Parameters
        ----
        file_name : str, optional
            The name of the Thumbnail file to load, by default None
        """

        # Grab the Adobe Application if it's open.
        try:
            self.adobe_app = win32.GetActiveObject("Illustrator.Application")
        except:
            self.adobe_app = win32.dynamic.Dispatch("Illustrator.Application")

        # Define the Thumbnail folder.
        self.thumbnail_folder = pathlib.Path("thumbnails").absolute()

        # If we have a file name open it.
        if file_name:

            # Create the full path.
            file_name = self.thumbnail_folder.joinpath(file_name)

            # Open the file.
            self.adobe_file = self.adobe_app.Open(file_name.as_posix())
        
        self.active_document = self.adobe_app.ActiveDocument

    @property
    def high_contrast_green(self) -> CDispatch:
        """Sets the Series color based on the series name.

        Returns
        -------
        (CDispatch):
            An `Illustrator.RGBColor` Object with the `Red`, `Blue` and `Green`
            property set.
        """

        # Define the Background Color Object.
        series_color = win32.Dispatch("Illustrator.RGBColor")
        series_color.Red = 7
        series_color.Green = 255
        series_color.Blue = 1

        return series_color

    @property
    def high_contrast_pink(self) -> CDispatch:
        """Sets the Series color based on the high contrast pink.

        Returns
        -------
        (CDispatch):
            An `Illustrator.RGBColor` Object with the `Red`, `Blue` and `Green`
            property set.
        """

        # Define the Background Color Object.
        series_color = win32.Dispatch("Illustrator.RGBColor")
        series_color.Red = 248
        series_color.Green = 5
        series_color.Blue = 254

        return series_color

    def add_character_style(self, name: str) -> CDispatch:
        """Either grabs the existing CharacterStyle or creates a new one.

        ## Parameters
        ----
        name : str
            The name of the series the video is part of.

        ## Returns
        ----
        (CDispatch):
            An `Illustrator.CharacterStyle` Object that represents the
            style for that particular video series.
        """

        # Define a new Character Style name based off the series name.
        new_name = "Series{series_name}CharacterStyle".format(
            series_name=name.capitalize()
        )

        # First try and grab it.
        try:

            title_character_style = self.active_document.CharacterStyles(
                new_name
            )

        # If that fails, then we don't have it so we need to create a new one.
        except:

            # Define a Character Style.
            title_character_style = self.active_document.CharacterStyles.Add(
                new_name
            )

            # Define the Character Attributes.
            title_character_attributes = title_character_style.CharacterAttributes
            title_character_attributes.Size = 60
            title_character_attributes.Leading = 84
            title_character_attributes.Tracking = 0

            # Define the Font.
            robot_text_font = self.adobe_app.TextFonts("Roboto-Bold")
            title_character_attributes.TextFont = robot_text_font

            # Set the Color.
            # title_character_style.FillColor = self.series_color

            print('Style did not Exist, created style {full_name}.'.format(
                full_name=new_name
            ))

        return title_character_style

    @property
    def background_black(self) -> CDispatch:
        """Represents the background color for the Thumbnail.

        ## Returns
        -------
        (CDispatch):
            An `Illustrator.RGBColor` Object with the `Red`, `Blue` and `Green`
            property set.
        """

        # Define the Background Color Object.
        black_background_color = win32.Dispatch("Illustrator.RGBColor")
        black_background_color.Red = 25
        black_background_color.Green = 24
        black_background_color.Blue = 24

        return black_background_color

    @property
    def foreground_white(self) -> CDispatch:
        """Represents the background color for the Thumbnail.

        ## Returns
        -------
        (CDispatch):
            An `Illustrator.RGBColor` Object with the `Red`, `Blue` and `Green`
            property set.
        """

        # Define the Text Font White Color.
        white_color = win32.Dispatch("Illustrator.RGBColor")
        white_color.Red = 255
        white_color.Green = 255
        white_color.Blue = 255

        return white_color

    def export_to_png(self, file_name: str) -> None:
        """Exports the Artboard as a PNG Image using the default settings.

        ## Parameters
        ----
        file_name : str
            The file path to location that you want to export to.
        """

        # Export the document.
        self.active_document.Export(
            ExportFile=file_name,
            ExportFormat=5,
            Options=self.export_options
        )

    @property
    def export_options(self) -> CDispatch:
        """Sets the PNG Export Options used to export the Artboard.

        ## Returns
        ----
        (CDispatch):
            An `Illustrator.ExportOptionsPNG24` Object with the `AntiAliasing`,
            `Transparency`, and `MatteColor` property set.
        """

        # Define the Export PNG24 Options.
        png_export_options = win32.Dispatch("Illustrator.ExportOptionsPNG24")
        png_export_options.AntiAliasing = True
        png_export_options.Transparency = True
        png_export_options.MatteColor = self.background_black
        png_export_options.VerticalScale = 101.0

        return png_export_options

    def thumbnail_layer(self) -> CDispatch:
        """Grabs the Thumbnail Layer from the Artboard.

        ## Returns
        ----
        (CDispatch):
            An `Illustrator.Layer` Object that represents the entire
            Thumbnail.
        """

        # Grab the Thumbnail Layer.
        thumbnail_layer = self.active_document.Layers("ThumbnailVideo")

        return thumbnail_layer

    def thumbnail_path(self) -> CDispatch:
        """Grabs the PathItem representing thumbnail background.

        ## Returns
        ----
        (CDispatch):
            An `Illustrator.PathItem` Object that represents the
            Thumbnail background color.
        """

        # Grab the Background.
        return self.thumbnail_layer().PathItems("ThumbnailBackground")

    def goal_subscriber_text_frame(self) -> CDispatch:
        """Grabs the PathItem representing GoalSubscriber Text Frame.

        ## Returns
        ----
        (CDispatch):
            An `Illustrator.TextFrame` Object that represents the
            GoalSubscriber Text Frame.
        """

        # Grab the Background.
        return self.thumbnail_layer().TextFrames("GoalSubscriber")

    def get_goal_subscriber_text_range(self) -> CDispatch:
        """Grabs the Text string inside of the TextRange belonging to the
        TextFrame.

        ## Returns
        ----
        (str):
            The Goal Subscriber raw Text.
        """

        # Grab the TextRange content.
        return self.goal_subscriber_text_frame().TextRange

    def set_goal_subscriber_text(self, text: str) -> None:
        """Set the Text for the Goal Subscriber."""

        # Set the Current Text.
        self.goal_subscriber_text_frame().TextRange.Contents = text

    def current_subscriber_text_frame(self) -> CDispatch:
        """Grabs the PathItem representing CurrentSubscriber Text Frame.

        ## Returns
        ----
        (CDispatch):
            An `Illustrator.TextFrame` Object that represents the
            CurrentSubscriber Text Frame.
        """

        # Grab the Background.
        return self.thumbnail_layer().TextFrames("CurrentSubscriber")

    def get_current_subscriber_text_range(self) -> CDispatch:
        """Grabs the Text string inside of the TextRange belonging to the
        TextFrame.

        ## Returns
        ----
        (str):
            The Current Subscriber raw Text.
        """

        # Grab the TextRange content.
        return self.current_subscriber_text_frame().TextRange

    def set_current_subscriber_text(self, text: str) -> None:
        """Set the Text for the Current Subscriber."""

        # Set the Current Text.
        self.current_subscriber_text_frame().TextRange.Contents = text

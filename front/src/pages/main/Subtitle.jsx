import React, { useContext } from "react";
import { VideoStateContext } from "../../context/AppWrapper";
import Box from "@mui/material/Box";

const Subtitle = ({ videoInfo }) => {
  // const videoState = useContext(VideoStateContext);
  return (
    <Box
      sx={{
        flexDirection: "column",
        display: "flex",
        overflow: "hidden",
        overflowY: "scroll", // added scroll
        margin: "auto",
        mr: 2,
        ml: 2,
        mb: 3,
        padding: 2,
        maxWidth: "95vh",
        height: "22.4rem", // backgroundColor: "#F2F2F2",
      }}>
      <p style={{
        color: 'black'
      }}>
        {videoInfo.subtitles}
      </p>
    </Box>
  );
};

export default Subtitle;

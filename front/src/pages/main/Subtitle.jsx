import React, { useContext } from "react";
import { useVideoState } from "../../context/AppWrapper";

import Box from "@mui/material/Box";

const Subtitle = () => {
  const videoState = useVideoState();

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
      }}
    >
      {videoState.subtitles}
      전체 자막
    </Box>
  );
};

export default Subtitle;

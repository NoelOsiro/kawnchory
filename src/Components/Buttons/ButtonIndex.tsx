import React from "react";
import styled from "styled-components";
export const XButton: React.FC = () => {
    return (
      <Group26>
        <RectangleCopy />
        
          <Rectangle />
          <RectangleCopy2 />
        
      </Group26>
    )
  }
  
  const Group26 = styled.div`
    height: 32px;
    width: 32px;
  `
  const RectangleCopy = styled.div`
    border-radius: 0px 4px 4px 0px;
    height: 32px;
    width: 32px;
    background-color: #5ca5a5;
    border: 0px solid #404040;
  `
  const Rectangle = styled.div`
    transform: rotate(-45deg);
    height: 16px;
    width: 3px;
    background-color: #ffffff;
    border: 0px solid #969696;
  `
  const RectangleCopy2 = styled.div`
    transform: rotate(-135deg);
    height: 16px;
    width: 3px;
    background-color: #ffffff;
    border: 0px solid #969696;
  `
  
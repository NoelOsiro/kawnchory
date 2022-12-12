import { Button, Col, Row } from "react-bootstrap"
import styled from "styled-components"
import SearchIcon from "../../assets/images/search.png";
import  Closer from "../../assets/images/close.svg";
import  CloserC from "../../assets/images/closerc.svg";

interface IFeat{
  active:boolean;
}

export const SearchBar = styled.div`
  position: relative;
  z-index:1;
  margin-top: -40px;
  height: 72px;
  margin-left: 165px;
  width:1110px;
  background: #FFFFFF;
  box-shadow: 0px 15px 20px -5px rgba(13, 113, 130, 0.15);
  border-radius: 5px;
`
export const SearchRow = styled(Row)`
  display: flex;
  flex-direction: row;
  justify-content: flex-start;
  height: 32px;
  padding: 20px 35px;
  align-items: center;
`
export const SearchOptionCol = styled(Col)`
    display:flex;
    flex-direction:row;
    margin-right: 20px;
    cursor:pointer;
`
export const SearchOptionText = styled.div`
    position: relative;
    font-family: 'League Spartan';
    font-style: normal;
    height:32px;
    font-weight: 700;
    font-size: 16px;
    line-height: 35px;
    letter-spacing: -0.123077px;
    padding-left: 5px;
    padding-right:5px;
    opacity:1;
    color: #5CA5A5;
    background-color: #5ca5a52f;
    border-radius:4px;
    z-index:2;  
`
export const SearchTag = styled.div`
  width:32px;
  height:32px;
  background:url(${Closer}) no-repeat;
  &:hover{
    background:url(${CloserC}) no-repeat;
  }
`
export const SearchForm = styled.form`
    filter: drop-shadow(6px 4px 6px rgba(99, 186, 186, 0.25));
    border-radius:50px;
    background: #FFFFFF;
    display: flex;
    align-items: center;
    border: 1px solid rgba(99, 186, 186, 0.4); 
    margin-left: 152px;
    margin-right:5px;
`
export const SearchInput = styled.input`
    border:none;
    border-radius:50px;
    width: 400px;
    height: 38px;   
    font-family: 'League Spartan';
    font-style: normal;
    font-weight: 700;
    font-size: 16px;
    text-align: start;
    padding-left: 23px;
    padding-right: 23px;
    &:focus {
    outline: none;
    border:none;
  }
`   
export const SubmitButton = styled(Button)`
    width: 44px;
    height: 29px;
    background:url(${SearchIcon}) no-repeat;
    border:none;
    cursor:pointer;
`

export const SearchOptionButton = styled(Button)`
  height: 32px;
  margin-top: 20px;
  margin-bottom: 20px;
  margin-left: 20px;
  background: #5ca5a52d;
  position:relative;
  z-index: 2;
  mix-blend-mode: normal;
  opacity: 1;
  border-radius: 4px;
  cursor:pointer;
`
export const ClearButton = styled(Button)`
    width: 45px;
    height: 24px;
    font-family: 'League Spartan';
    font-style: normal;
    font-weight: 700;
    font-size: 16px;
    line-height: 24px;
    text-align: center;
    letter-spacing: -0.123077px;
    text-decoration-line: underline;
    background-color: white;
    color: #5CA5A5;
    border:none;
    cursor:pointer;
`

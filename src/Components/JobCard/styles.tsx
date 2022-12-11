import { Card, Row, Image, Col } from "react-bootstrap";
import styled from "styled-components";

export const CardRow = styled(Card)`
    width: 1110px;
    height: 152px; 
    background: #FFFFFF;
    box-shadow: 0px 15px 20px -5px rgba(13, 113, 130, 0.15);
    border-radius: 5px;
    border-left: 3px solid  #5CA5A5;
    display: flex;
`
export const CardContent = styled(Row)`
    display: flex;
    width: 1030px;
    height: 89px;
    margin-top:32px;
    margin-bottom:31px;
    margin-left: 40px;
    margin-right:40px;

`
export const CardLogo = styled(Image)`
    border-radius: 50%;
    width: 88px;
    height:88px;
`
export const CardDesc = styled(Col)`
    width: 262px;
    height: 89px; 
    margin-left: 24px;
`
export const CompanyTitle = styled.div`
    height:17px;
    font-family: 'League Spartan';
    font-style: normal;
    font-weight: 700;
    font-size: 18px;
    line-height: 17px;
    color: #5CA5A5;
`
export const CardTraits = styled.div`
    display:flex;
    align-items:center;
    width: 138px;
    height: 24px;
    margin-left: 15px;
    margin-right:23px;
`
export const JobTitle = styled.p`
    height: 24px;
    font-family: 'League Spartan';
    font-style: normal;
    font-weight: 700;
    font-size: 22px;
    line-height: 24px;
    color: #2B3939;
`
export const FeatRow = styled(Row)`
    height:24px;
    display:flex;
    align-items:center;
    margin-bottom:10px;
`
export const StatusRow = styled(FeatRow)`
    margin-bottom:0px;
        display: flex;
`
export const StatusRowList = styled.ul`
    display: flex;
    align-items: center;
    padding-left: 0px;
    margin: 0;
    flex-wrap: wrap;
`
export const StatusListItem = styled.li`
    margin-right:30px;
`
export const StatusListItem1 = styled(StatusListItem)`
    list-style:none;
`
export const StatusListItem2 = styled(StatusListItem)`
    margin-right:0px;
`

export const CardTraitElement = styled.div`
    background: #5CA5A5;
    border-radius: 12px;
    align-items: center;
    display: flex;
    justify-content: center;
    width:51px;
    height:24px;
    font-family: 'League Spartan';
    font-style: normal;
    font-weight: 700;
    font-size: 14px;
    line-height: 16px;
    text-align: center;
    letter-spacing: -0.107692px;
    text-transform: uppercase;
    color: #FFFFFF;
    padding-left: 2px;
    padding-right: 2px;
    padding-top: 2px;
`
export const CardTraitFeatElement = styled(CardTraitElement)`
    background: #000000;
    width:82px;
    margin-left:14px;
`
export const CardDetails = styled.div`
    font-family: 'League Spartan';
    font-style: normal;
    font-weight: 500;
    font-size: 18px;
    line-height: 24px;
    letter-spacing: -0.138462px;
    height: 24px;
    color: #7C8F8F;

`
export const JobTraitList = styled.ul`
    position: absolute;
    left: rigth;
    width: 400px;
    height: 32px;
    left: 835px;
    top: 273px;
    display: flex;
    flex-direction: row;
    align-items: center;
    font-family: 'League Spartan';
    font-style: normal;
    font-weight: 700;
    font-size: 16px;
    line-height: 24px;
    text-align: center;
    letter-spacing: -0.123077px;
    color: #5CA5A5;
    list-style: none;
    text-align: center;
`
export const JobTraitListItem = styled.li`
    background: #eff6f6;
    mix-blend-mode: normal;
    border-radius: 4px;
    padding:6px;
    margin-right:16px;
`
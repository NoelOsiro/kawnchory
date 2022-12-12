import React from 'react';
import { SearchBar, SearchOptionCol, SearchOptionText, SearchRow, SearchInput,SearchForm, SubmitButton, ClearButton, SearchTag } from './styles';
import {ReactComponent as Close} from "../../assets/images/close.svg";



export interface IProps {
  change:(e:React.ChangeEvent<HTMLInputElement>)=> void;
  clickFilter:(e:React.MouseEvent<HTMLDivElement, MouseEvent>)=>void;
}

const FilterBar:React.FC<IProps> = (props:IProps) => {
  
  return (
    <SearchBar>
        <SearchRow>
            <SearchOptionCol>
            <SearchOptionText onClick={props.clickFilter}>Frontend</SearchOptionText>
            <SearchTag/>
            </SearchOptionCol>
            <SearchOptionCol>
            <SearchOptionText onClick={props.clickFilter}>CSS</SearchOptionText>
            <SearchTag/>
            </SearchOptionCol>
            <SearchOptionCol>
            <SearchOptionText onClick={props.clickFilter}>JavaScript</SearchOptionText>
            <SearchTag/>
            </SearchOptionCol>
            <SearchForm>
            <SearchInput name="search" type='text' 
            id="searchInput" placeholder='search...' 
            onChange={props.change}/>
            <SubmitButton type="submit"/>
            </SearchForm>
            <ClearButton>Clear</ClearButton> 
        </SearchRow>
    </SearchBar>
  )
}

export default FilterBar
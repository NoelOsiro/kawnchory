import React from 'react';
import { SearchBar, SearchOptionCol, SearchOptionText, SearchRow, SearchInput,SearchForm, SubmitButton, ClearButton } from './styles';
import {ReactComponent as Close} from "../../assets/images/close.svg";


interface IProps {
  change:(e:React.ChangeEvent<HTMLInputElement>)=> void;
}

const FilterBar:React.FC<IProps> = (props:IProps) => {
  
  return (
    <SearchBar>
        <SearchRow>
            <SearchOptionCol>
            <SearchOptionText>Frontend</SearchOptionText>
            <Close/>
            </SearchOptionCol>
            <SearchOptionCol>
            <SearchOptionText>CSS</SearchOptionText>
            <Close/>
            </SearchOptionCol>
            <SearchOptionCol>
            <SearchOptionText>JavaScript</SearchOptionText>
            <Close/>
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
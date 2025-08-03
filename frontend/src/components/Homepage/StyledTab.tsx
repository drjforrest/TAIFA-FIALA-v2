import styled from "styled-components";
import { Tab } from "react-tabs";
import { COLORS } from "@/constants/colors"; // Using @/ alias

const StyledTab = styled(Tab)`
  padding: 10px 20px;
  color: ${COLORS.gray[300]};
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.3s;

  &:hover {
    color: ${COLORS.cyan[400]};
  }

  &.react-tabs__tab--selected {
    color: ${COLORS.cyan[400]};
    border-bottom: 2px solid ${COLORS.cyan[400]};
  }
`;

export default StyledTab;

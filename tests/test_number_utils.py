"""Tests for line model and hierarchical number detection."""


from fastpdf4llm.utils.number_utils import is_hierarchical_number


class TestIsHierarchicalNumber:
    """Test cases for is_hierarchical_number function."""

    # Pattern 1: Arabic numerals with dots
    def test_arabic_numerals_basic(self):
        """Test basic Arabic numeral formats."""
        assert is_hierarchical_number("1") is False
        assert is_hierarchical_number("2") is False
        assert is_hierarchical_number("10") is False
        assert is_hierarchical_number("123") is False

    def test_arabic_numerals_with_dot(self):
        """Test Arabic numerals with trailing dot."""
        assert is_hierarchical_number("1.") is True
        assert is_hierarchical_number("2.") is True
        assert is_hierarchical_number("10.") is True

    def test_arabic_numerals_hierarchical(self):
        """Test hierarchical Arabic numerals."""
        assert is_hierarchical_number("1.1") is True
        assert is_hierarchical_number("1.2.3") is True
        assert is_hierarchical_number("2.10.3") is True
        assert is_hierarchical_number("1.2.3.") is True

    def test_arabic_numerals_with_chinese_punctuation(self):
        """Test Arabic numerals with Chinese punctuation."""
        assert is_hierarchical_number("1、") is True
        assert is_hierarchical_number("1.1、") is True
        assert is_hierarchical_number("2.10.3、") is True

    # Pattern 2: Chinese numerals
    def test_chinese_numerals_basic(self):
        """Test basic Chinese numeral formats."""
        assert is_hierarchical_number("一") is False
        assert is_hierarchical_number("二") is False
        assert is_hierarchical_number("三") is False
        assert is_hierarchical_number("十") is False

    def test_chinese_numerals_with_punctuation(self):
        """Test Chinese numerals with punctuation."""
        assert is_hierarchical_number("一、") is True
        assert is_hierarchical_number("二、") is True
        assert is_hierarchical_number("三、") is True
        assert is_hierarchical_number("十、") is True

    def test_chinese_numerals_all(self):
        """Test all Chinese numerals."""
        chinese_nums = ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十"]
        for num in chinese_nums:
            assert is_hierarchical_number(num) is False
            assert is_hierarchical_number(f"{num}、") is True

    # Pattern 3: Parentheses with Arabic numerals
    def test_parentheses_arabic_halfwidth(self):
        """Test half-width parentheses with Arabic numerals."""
        assert is_hierarchical_number("(1)") is True
        assert is_hierarchical_number("(2)") is True
        assert is_hierarchical_number("(1.1)") is True
        assert is_hierarchical_number("(2.10.3)") is True

    def test_parentheses_arabic_fullwidth(self):
        """Test full-width parentheses with Arabic numerals."""
        assert is_hierarchical_number("（1）") is True
        assert is_hierarchical_number("（2）") is True
        assert is_hierarchical_number("（1.1）") is True
        assert is_hierarchical_number("（2.10.3）") is True

    def test_parentheses_arabic_with_punctuation(self):
        """Test parentheses with Arabic numerals and punctuation."""
        assert is_hierarchical_number("（1)、") is True
        assert is_hierarchical_number("(1)、") is True
        assert is_hierarchical_number("（1.1)、") is True
        assert is_hierarchical_number("(1.1)、") is True

    # Pattern 4: Parentheses with Chinese numerals
    def test_parentheses_chinese_halfwidth(self):
        """Test half-width parentheses with Chinese numerals."""
        assert is_hierarchical_number("(一)") is True
        assert is_hierarchical_number("(二)") is True
        assert is_hierarchical_number("(十)") is True

    def test_parentheses_chinese_fullwidth(self):
        """Test full-width parentheses with Chinese numerals."""
        assert is_hierarchical_number("（一）") is True
        assert is_hierarchical_number("（二）") is True
        assert is_hierarchical_number("（十）") is True

    def test_parentheses_chinese_with_punctuation(self):
        """Test parentheses with Chinese numerals and punctuation."""
        assert is_hierarchical_number("（一）、") is True
        assert is_hierarchical_number("(一)、") is True
        assert is_hierarchical_number("（二）、") is True

    # Pattern 5: Square brackets with Arabic numerals
    def test_square_brackets_arabic_halfwidth(self):
        """Test half-width square brackets with Arabic numerals."""
        assert is_hierarchical_number("[1]") is True
        assert is_hierarchical_number("[2]") is True
        assert is_hierarchical_number("[1.1]") is True
        assert is_hierarchical_number("[2.10.3]") is True

    def test_square_brackets_arabic_fullwidth(self):
        """Test full-width square brackets with Arabic numerals."""
        assert is_hierarchical_number("【1】") is True
        assert is_hierarchical_number("【2】") is True
        assert is_hierarchical_number("【1.1】") is True
        assert is_hierarchical_number("【2.10.3】") is True

    def test_square_brackets_arabic_with_punctuation(self):
        """Test square brackets with Arabic numerals and punctuation."""
        assert is_hierarchical_number("[1]、") is True
        assert is_hierarchical_number("【1】、") is True
        assert is_hierarchical_number("[1.1]、") is True
        assert is_hierarchical_number("【1.1】、") is True

    # Pattern 6: Square brackets with Chinese numerals
    def test_square_brackets_chinese_halfwidth(self):
        """Test half-width square brackets with Chinese numerals."""
        assert is_hierarchical_number("[一]") is True
        assert is_hierarchical_number("[二]") is True
        assert is_hierarchical_number("[十]") is True

    def test_square_brackets_chinese_fullwidth(self):
        """Test full-width square brackets with Chinese numerals."""
        assert is_hierarchical_number("【一】") is True
        assert is_hierarchical_number("【二】") is True
        assert is_hierarchical_number("【十】") is True

    def test_square_brackets_chinese_with_punctuation(self):
        """Test square brackets with Chinese numerals and punctuation."""
        assert is_hierarchical_number("[一]、") is True
        assert is_hierarchical_number("【一】、") is True
        assert is_hierarchical_number("[二]、") is True
        assert is_hierarchical_number("【二】、") is True

    # Edge cases
    def test_whitespace_handling(self):
        """Test that whitespace is properly stripped."""
        assert is_hierarchical_number("  1  ") is True
        assert is_hierarchical_number("  1.1  ") is True
        assert is_hierarchical_number("  一、  ") is True
        assert is_hierarchical_number("  (1)  ") is True
        assert is_hierarchical_number("  [1]  ") is True
        assert is_hierarchical_number("  【一】  ") is True

    def test_empty_string(self):
        """Test that empty strings return False."""
        assert is_hierarchical_number(None) is False
        assert is_hierarchical_number("") is False
        assert is_hierarchical_number("   ") is False
        assert is_hierarchical_number("\t") is False
        assert is_hierarchical_number("\n") is False

    def test_invalid_formats(self):
        """Test that invalid formats return False."""
        # Invalid: leading zeros
        assert is_hierarchical_number("01") is False
        assert is_hierarchical_number("01.1") is True

        # Invalid: letters mixed with numbers
        assert is_hierarchical_number("1a") is False
        assert is_hierarchical_number("a1") is False
        assert is_hierarchical_number("1.1a") is True

        # Invalid: wrong punctuation
        assert is_hierarchical_number("1,") is False
        assert is_hierarchical_number("1;") is False
        assert is_hierarchical_number("1:") is False

        # Invalid: incomplete parentheses/brackets
        assert is_hierarchical_number("(1") is False
        assert is_hierarchical_number("1)") is False
        assert is_hierarchical_number("[1") is False
        assert is_hierarchical_number("1]") is False

        # Invalid: mixed formats
        assert is_hierarchical_number("(1.1)") is True  # This is valid
        assert is_hierarchical_number("1.1.1.1.1.1.1.1.1.1.1") is True  # This is valid
        assert is_hierarchical_number("一.1") is True  # Mixed Chinese and Arabic
        assert is_hierarchical_number("1.一") is True  # Mixed Arabic and Chinese

        # Invalid: special characters
        assert is_hierarchical_number("1#") is False
        assert is_hierarchical_number("@1") is False
        assert is_hierarchical_number("1$") is False

        # Invalid: only punctuation
        assert is_hierarchical_number(".") is False
        assert is_hierarchical_number("、") is False
        assert is_hierarchical_number("()") is False
        assert is_hierarchical_number("[]") is False
        assert is_hierarchical_number("【】") is False

    def test_complex_hierarchical_numbers(self):
        """Test complex hierarchical number formats."""
        # Deep nesting
        assert is_hierarchical_number("1.2.3.4.5") is True
        assert is_hierarchical_number("1.2.3.4.5.") is True
        assert is_hierarchical_number("1.2.3.4.5、") is True

        # Large numbers
        assert is_hierarchical_number("100") is False
        assert is_hierarchical_number("100.200.300") is True
        assert is_hierarchical_number("(100)") is True
        assert is_hierarchical_number("[100]") is True

    def test_mixed_parentheses_brackets(self):
        """Test that mixed parentheses and brackets are invalid."""
        assert is_hierarchical_number("(1]") is False
        assert is_hierarchical_number("[1)") is False
        assert is_hierarchical_number("（1]") is False
        assert is_hierarchical_number("[1）") is False

    def test_real_world_examples(self):
        """Test real-world examples that should be recognized."""
        # Common document formats
        assert is_hierarchical_number("1.") is True  # Section 1
        assert is_hierarchical_number("1.1") is True  # Subsection 1.1
        assert is_hierarchical_number("一、") is True  # Chinese section
        assert is_hierarchical_number("（1）") is True  # Chinese parentheses
        assert is_hierarchical_number("[1]") is True  # Reference format
        assert is_hierarchical_number("【一】") is True  # Chinese brackets

/**
 * @Author: chentong
 * @Date: 2025/02/08 12:37
 */

package tools

import (
	"bytes"
	"crypto/tls"
	"encoding/base64"
	"errors"
	"io"
	"mime/multipart"
	"net/http"
	"strings"

	"github.com/disintegration/imaging"
)

func resizeImg2Base64(r io.Reader, width, height int) (base64Str string, err error) {
	img, err := imaging.Decode(r, imaging.AutoOrientation(true))
	if err != nil {
		return
	}

	var buf bytes.Buffer
	resize := imaging.Resize(img, width, height, imaging.Lanczos)
	if err = imaging.Encode(&buf, resize, imaging.PNG); err != nil {
		return
	}

	base64Str = base64.StdEncoding.EncodeToString(buf.Bytes())

	return
}

// ResizeMultipartImgToBase64 将multipart.FileHeader表示的图片文件调整大小，并以base64编码字符串的形式返回。
// 参数f是包含图片文件信息的multipart.FileHeader指针；
// 参数width和height分别是目标图片的宽度和高度。
// 返回值base64Str是调整大小后的图片的base64编码字符串；err是错误信息，如果执行过程中发生错误则不为nil。
func ResizeMultipartImgToBase64(f *multipart.FileHeader, width, height int) (base64Str string, err error) {
	file, err := f.Open()
	if err != nil {
		return
	}
	defer file.Close()

	return resizeImg2Base64(file, width, height)
}

// ResizeURLImgToBase64 从指定的URL获取图像，并将其调整为指定的宽度和高度后，转换为Base64编码的字符串。
// 参数:
//
//	url - 图像的URL地址。
//	width - 调整后图像的宽度。
//	height - 调整后图像的高度。
//
// 返回值:
//
//	base64Str - 转换后的Base64编码字符串。
//	err - 错误信息，如果执行过程中遇到任何错误，则返回该错误。
func ResizeURLImgToBase64(url string, width, height int) (base64Str string, err error) {
	client := &http.Client{
		Transport: &http.Transport{
			TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
		},
	}

	resp, err := client.Get(url)
	if err != nil {
		return
	}
	defer resp.Body.Close()

	return resizeImg2Base64(resp.Body, width, height)
}

// resizeBytes2Base64 将原始图片字节缩放为指定尺寸并返回完整 data-URI (PNG)。
func resizeBytes2Base64(raw []byte, width, height int) (string, error) {
	b64, err := resizeImg2Base64(bytes.NewReader(raw), width, height)
	if err != nil {
		return "", err
	}
	return "data:image/png;base64," + b64, nil
}

// IconInputToBase64 将后台传入的图标输入统一规范为完整 data:image/png;base64, 形式。
// 支持三种输入：
//  1. http(s):// 开头的图片 URL —— 下载后转 base64
//  2. data:image/... 开头的完整 data-URI —— 提取 base64 部分缩放
//  3. 裸 base64（PNG 以 iVBORw0KG 开头 / JPEG 以 /9j/ 开头）—— 自动补 data: 前缀后缩放
//
// 无法识别或处理失败时返回空字符串，由调用方决定回退默认图标。
// 其它格式（如 linecons 类名）原样返回，保持兼容。
func IconInputToBase64(input string, width, height int) (string, error) {
	s := strings.TrimSpace(input)
	if s == "" {
		return "", nil
	}

	// 1) 已是完整 data-URI
	if strings.HasPrefix(s, "data:") {
		idx := strings.Index(s, ",")
		if idx < 0 {
			return "", errors.New("invalid data uri")
		}
		raw, err := base64.StdEncoding.DecodeString(s[idx+1:])
		if err != nil {
			return "", err
		}
		return resizeBytes2Base64(raw, width, height)
	}

	// 2) http(s) URL -> 下载
	if strings.HasPrefix(s, "http://") || strings.HasPrefix(s, "https://") {
		return ResizeURLImgToBase64(s, width, height)
	}

	// 3) 裸 base64：PNG / JPEG 自动补前缀
	if strings.HasPrefix(s, "iVBORw0KG") || strings.HasPrefix(s, "/9j/") {
		raw, err := base64.StdEncoding.DecodeString(s)
		if err != nil {
			return "", err
		}
		return resizeBytes2Base64(raw, width, height)
	}

	// 4) 其它（linecons 类名等）保持原样
	return s, nil
}

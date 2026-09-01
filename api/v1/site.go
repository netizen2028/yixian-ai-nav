/**
 * @Author: chentong
 * @Date: 2024/05/27 下午6:19
 */

package v1

import (
	"mime/multipart"

	excelize "github.com/xuri/excelize/v2"
)

type Site struct {
	Id          int    `json:"id"`               // ID
	Icon        string `json:"icon"`             // 网站 logo
	Title       string `json:"title"`            // 名称简介
	Url         string `json:"url"`              // 链接
	Category    string `json:"category"`         // 分类
	CategoryId  int    `json:"category_id"`      // 分类id
	Description string `json:"description"`      // 描述
	Tag         string `json:"tag"`              // 自定义标签文字（如：超导 / 量子通讯 / 自定义）
	TagColor    string `json:"tag_color"`        // 自定义标签颜色（十六进制，如 #1f6feb；为空则用路线默认配色）
	IsUsed      bool   `json:"is_used"`          // 是否启用
	Sort        int    `json:"sort" form:"sort"` // 排序
	CreatedAt   string `json:"created_at"`       // 创建时间
	UpdatedAt   string `json:"updated_at"`       // 更新时间
}

type (
	SiteDeleteReq struct {
		ID int `uri:"id" binding:"required"` // ID
	}

	SiteDeleteResp struct {
		ID int `json:"id"` // ID
	}
)

type (
	SiteLisPagination struct {
		Total        int64 `json:"total"`          // 总数
		CurrentPage  int   `json:"current_page"`   // 当前页
		PerPageCount int   `json:"per_page_count"` // 每页显示条数
	}

	SiteListReq struct {
		Page       int    `form:"page,default=1"`        // 第几页
		PageSize   int    `form:"page_size,default=10" ` // 每页显示条数
		Search     string `form:"search"`                // 搜索关键字
		CategoryID int    `form:"category_id"`           // 分类ID
	}

	SiteListResp struct {
		List       []Site            `json:"list"`       // 列表网站信息
		Pagination SiteLisPagination `json:"pagination"` // 分页信息
	}
)

type (
	SiteCreateReq struct {
		CategoryID int    `form:"category_id"` // 类别ID
		Url        string `form:"url"`         // 网址地址
		IsUsed     bool   `form:"is_used"`     // 是否启用
		FailSwitch bool   `form:"fail_switch"` // 失败开关
		Tag        string `form:"tag"`         // 自定义标签文字
		TagColor   string `form:"tag_color"`   // 自定义标签颜色
	}

	SiteCreateResp struct {
		SuccessCount int      `json:"successCount"` // 成功计数
		FailCount    int      `json:"failCount"`    // 失败计数
		FailURLs     []string `json:"failURLs"`     // 失败URL
	}
)

type (
	SiteUpdateReq struct {
		Id          int                   `json:"id" uri:"id"`                    // ID
		Icon        string                `json:"thumb" form:"thumb"`             // 网站 logo
		Title       string                `json:"title" form:"title"`             // 名称简介
		Url         string                `json:"url" form:"url"`                 // 链接
		CategoryId  int                   `json:"category_id" form:"category_id"` // 分类id
		Description string                `json:"description" form:"description"` // 描述
		Tag         *string               `json:"tag" form:"tag"`                 // 自定义标签文字（指针：nil=不改，空串=清空）
		TagColor    *string               `json:"tag_color" form:"tag_color"`     // 自定义标签颜色（指针：nil=不改，空串=清空）
		IsUsed      *bool                 `json:"is_used" form:"is_used"`         // 是否启用
		File        *multipart.FileHeader `json:"file" form:"file"`               // 上传 logo 图片
		Sort        int                   `json:"sort" form:"sort"`               // 排序
	}

	SiteUpdateResp struct {
		ID int `json:"id"` // 主键ID
	}
)

type (
	SiteSyncReq struct {
		ID int `uri:"id"` // 主键ID
	}
	SiteSyncResp struct {
		ID int `json:"id"` // 主键ID
	}
)

type (
	SiteExportReq struct {
		Search     string `json:"search" form:"search"`           // 搜索关键字
		CategoryID int    `json:"category_id" form:"category_id"` // 分类ID
	}

	SiteExportResp struct {
		File *excelize.File
	}
)

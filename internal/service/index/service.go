/**
 * @Author: chentong
 * @Date: 2024/05/26 上午1:48
 */

package index

import (
	"context"

	"github.com/gin-gonic/gin"

	v1 "github.com/ch3nnn/webstack-go/api/v1"
	"github.com/ch3nnn/webstack-go/internal/dal/repository"
	s "github.com/ch3nnn/webstack-go/internal/service"
)

var _ Service = (*service)(nil)

type Service interface {
	i()

	// Index 首页，categoryID 为 ?category=N 传入的分类ID（0 表示未筛选）
	Index(ctx context.Context, categoryID int) (*v1.IndexResp, error)
	// About 关于我
	About(ctx *gin.Context) (*v1.AboutResp, error)
}

type service struct {
	*s.Service
	siteRepo     repository.IStSiteDao
	categoryRepo repository.IStCategoryDao
	configRepo   repository.ISysConfigDao
}

func NewService(
	s *s.Service,
	siteRepo repository.IStSiteDao,
	categoryRepo repository.IStCategoryDao,
	configRepo repository.ISysConfigDao,
) Service {
	return &service{
		Service:      s,
		siteRepo:     siteRepo,
		categoryRepo: categoryRepo,
		configRepo:   configRepo,
	}
}

func (s *service) i() {}
